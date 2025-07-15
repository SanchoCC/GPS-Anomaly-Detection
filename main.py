import os
import json
import subprocess
import time
import math
import shutil
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from openai import OpenAI

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INPUT_FILES = ["points.json", "points2.json", "points3.json"]
MAX_ITERATIONS = 15
CPP_COMPILER = "g++"
BASE_OUTPUT_NAME = "gps_algorithm"
RESULTS_DIR = "iteration_results"
COMPILED_DIR = "compiled_binaries"
CORRECTED_DIR = "corrected_data"
MAX_CODE_LENGTH = 15000
CPP_SOURCE = os.path.join(COMPILED_DIR, "current_iteration.cpp")

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


class TestResult:
    def __init__(self):
        self.iteration = 0
        self.timestamp = datetime.now().isoformat()
        self.compile_success = False
        self.anomaly_detected = False
        self.correction_success = False
        self.execution_time = 0.0
        self.algorithm_code = ""
        self.ai_feedback = ""
        self.errors = ""
        self.input_file = ""
        self.details = {
            "code_size": 0,
            "compile_time": 0.0,
            "memory_usage": 0,
            "test_cases_passed": 0,
            "binary_size": 0,
            "unchanged_points": 0,
            "changed_points": 0,
            "time_mismatches": 0
        }


def setup_environment():
    """Create necessary directories for results"""
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(COMPILED_DIR, exist_ok=True)
    os.makedirs(CORRECTED_DIR, exist_ok=True)


def clean_environment():
    """Clean up previous runs"""
    if os.path.exists(RESULTS_DIR):
        shutil.rmtree(RESULTS_DIR)
    if os.path.exists(COMPILED_DIR):
        shutil.rmtree(COMPILED_DIR)
    if os.path.exists(CORRECTED_DIR):
        shutil.rmtree(CORRECTED_DIR)
    setup_environment()


def validate_code_structure(code: str) -> Optional[str]:
    """Check for common issues before compilation"""
    required_components = [
        (r"std\s*::\s*setprecision", "#include <iomanip>"),
        (r"std\s*::\s*stringstream", "#include <sstream>"),
        (r"std\s*::\s*vector", "#include <vector>"),
        (r"std\s*::\s*(sqrt|fabs|pow)", "#include <cmath>"),
        (r"M_PI", "#define _USE_MATH_DEFINES")
    ]

    for pattern, requirement in required_components:
        if re.search(pattern, code) and requirement not in code:
            return f"Missing '{requirement}' required for pattern '{pattern}'"

    if "using namespace std;" in code:
        return "Avoid 'using namespace std;' - use std:: prefix instead"

    # Check for basic JSON parsing capability
    json_patterns = [
        r"std\s*::\s*string\s+line",
        r"std\s*::\s*getline\s*\(\s*std\s*::\s*cin",
        r"std\s*::\s*stoi"
    ]
    if not any(re.search(p, code) for p in json_patterns):
        return "Missing essential JSON parsing components"

    # Check for anomaly detection logic
    anomaly_patterns = [
        r"distance\s*[<>=]",
        r"speed\s*[<>=]",
        r"interpolat"
    ]
    if not any(re.search(p, code, re.IGNORECASE) for p in anomaly_patterns):
        return "Missing essential anomaly detection or interpolation logic"

    return None


def calculate_distance(lat1: int, lon1: int, lat2: int, lon2: int) -> float:
    """Calculate distance between two GPS points in meters using Haversine formula"""
    lat1, lon1, lat2, lon2 = lat1 / 1e6, lon1 / 1e6, lat2 / 1e6, lon2 / 1e6

    R = 6371000  # Earth radius in meters
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) * math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def analyze_results(input_data: List[Dict], output_data: List[Dict]) -> Tuple[bool, Dict]:
    """Check if output data meets quality criteria with enhanced validation"""
    analysis = {
        "remaining_anomalies": 0,
        "max_speed_violations": 0,
        "time_reversals": 0,
        "point_count_match": len(input_data) == len(output_data),
        "unchanged_points": 0,
        "changed_points": 0,
        "time_mismatches": 0,
        "invalid_changes": 0
    }

    # Basic length check
    if not analysis["point_count_match"]:
        return False, analysis

    # Check time stamps consistency
    for i in range(len(input_data)):
        if input_data[i]["time"] != output_data[i]["time"]:
            analysis["time_mismatches"] += 1

    # Track point changes
    max_speed = 50  # m/s (180 km/h)
    valid_output = True
    unchanged_points = 0

    for i in range(len(input_data)):
        input_point = input_data[i]
        output_point = output_data[i]

        # Only coordinates should change, time must remain the same
        if (input_point["lat"] == output_point["lat"] and
                input_point["lon"] == output_point["lon"]):
            unchanged_points += 1
        else:
            analysis["changed_points"] += 1
            # Check if change was actually needed
            if i > 0 and i < len(input_data) - 1:
                prev_dist = calculate_distance(
                    input_data[i - 1]["lat"], input_data[i - 1]["lon"],
                    input_point["lat"], input_point["lon"]
                )
                next_dist = calculate_distance(
                    input_point["lat"], input_point["lon"],
                    input_data[i + 1]["lat"], input_data[i + 1]["lon"]
                )
                prev_time = input_point["time"] - input_data[i - 1]["time"]
                next_time = input_data[i + 1]["time"] - input_point["time"]

                if prev_time > 0 and next_time > 0:
                    prev_speed = prev_dist / prev_time
                    next_speed = next_dist / next_time
                    if prev_speed <= max_speed and next_speed <= max_speed:
                        analysis["invalid_changes"] += 1

    analysis["unchanged_points"] = unchanged_points

    # Check for anomalies in output
    for i in range(1, len(output_data)):
        prev = output_data[i - 1]
        curr = output_data[i]
        time_diff = curr["time"] - prev["time"]

        if time_diff <= 0:
            analysis["time_reversals"] += 1
            valid_output = False
        else:
            distance = calculate_distance(prev["lat"], prev["lon"], curr["lat"], curr["lon"])
            speed = distance / time_diff
            if speed > max_speed:
                analysis["max_speed_violations"] += 1
                valid_output = False

    analysis["remaining_anomalies"] = analysis["max_speed_violations"] + analysis["time_reversals"]

    # Final validation
    correction_success = (
            valid_output and
            analysis["time_mismatches"] == 0 and
            analysis["invalid_changes"] == 0 and
            analysis["remaining_anomalies"] == 0
    )

    return correction_success, analysis


def generate_initial_prompt() -> str:
    return """Write a C++ program for GPS anomaly detection with these REQUIREMENTS:

1. MUST INCLUDE these headers:
#include <iostream>
#include <vector>
#include <cmath>
#include <algorithm>
#include <iomanip>
#include <sstream>
#define _USE_MATH_DEFINES

2. Technical Specifications:
- Use C++17 standard
- Input: JSON array of {"lat":int,"lon":int,"time":int} from stdin
- Output: Corrected JSON to stdout in same format
- Detect anomalies using speed thresholds (max 50 m/s)
- Implement linear interpolation ONLY for anomalous points
- Non-anomalous points MUST remain unchanged
- Time stamps MUST remain unchanged
- Only change coordinates of anomalous points

3. Critical Requirements:
- Read entire input from stdin until EOF
- Parse JSON manually (no external libraries)
- Use std:: prefix for all standard functions
- Output must be valid JSON array
- Max code length: 15000 characters
- ONLY change points with impossible speeds (over 50 m/s)
- NEVER change first and last points

4. Research Requirements:
- Search for optimal GPS anomaly detection algorithms
- Consider both speed-based and statistical approaches
- Implement the most robust solution found

Example input: 
[{"lat":48480512,"lon":32271152,"time":1743465601},{"lat":48480008,"lon":32271596,"time":1743465606}]

Example output:
[{"lat":48480512,"lon":32271152,"time":1743465601},{"lat":48480008,"lon":32271596,"time":1743465606}]

Provide ONLY the compilable C++ code with no additional text."""


def generate_improvement_prompt(previous_code: str, errors: str, execution_stats: Dict, feedback: str) -> str:
    return f"""Improve this GPS correction code based on SPECIFIC ISSUES:

1. FIX THESE ERRORS FIRST:
{errors}

2. Previous Performance:
- Success rate: {execution_stats.get('passed', 0)}/{execution_stats.get('total', 3)}
- Avg time: {execution_stats.get('avg_time', 0):.2f}s
- Best time: {execution_stats.get('best_time', 0):.2f}s

3. REQUIRED IMPROVEMENTS:
- Ensure complete input reading from stdin
- Validate JSON parsing handles all cases
- Fix any compilation errors
- Maintain consistent JSON output format
- Only change anomalous points (speed > 50 m/s)
- Never change time stamps
- Keep non-anomalous points unchanged
- Never change first and last points
- Add proper error handling
- Research and implement better anomaly detection if needed

4. Research Requirements:
- Search for academic papers or articles on GPS anomaly detection
- Consider implementing Kalman filters or other advanced techniques
- Optimize for both accuracy and performance

5. Input/Output SPEC:
- Input: JSON array of objects with "lat","lon","time" (integers)
- Output: Corrected JSON array in same format
- Time stamps MUST remain unchanged
- Only coordinates of anomalous points should be modified

6. CRITICAL ISSUES FROM LAST RUN:
{feedback}

7. CODE TO IMPROVE (first 200 chars):
{previous_code[:200]}...

Provide ONLY the complete corrected C++ code with:
1. All required headers
2. Fixed namespace issues
3. No external dependencies
4. No additional commentary"""


def save_iteration_artifacts(iteration: int, code: str, binary_path: str):
    """Save both source code and compiled binary for the iteration"""
    # Save source code
    code_filename = os.path.join(RESULTS_DIR, f"iteration_{iteration}_code.cpp")
    with open(code_filename, "w", encoding="utf-8") as f:
        f.write(code)

    # Save binary
    if os.path.exists(binary_path):
        binary_filename = os.path.join(RESULTS_DIR, f"iteration_{iteration}_binary")
        shutil.copy2(binary_path, binary_filename)
        os.chmod(binary_filename, 0o755)


def save_corrected_data(input_file: str, iteration: int, corrected_points: List[Dict]):
    """Save corrected GPS points to a file"""
    filename = os.path.join(
        CORRECTED_DIR,
        f"iter_{iteration}_{os.path.basename(input_file)}"
    )
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(corrected_points, f, indent=2)


def sanitize_code(raw_code: str) -> str:
    """Extract C++ code from AI response"""
    if "```cpp" in raw_code:
        return raw_code.split("```cpp")[1].split("```")[0]
    elif "```" in raw_code:
        return raw_code.split("```")[1].split("```")[0]
    return raw_code


def validate_json_output(output: str) -> bool:
    """Validate JSON structure without parsing full content"""
    if not output.strip().startswith("["):
        return False
    if not output.strip().endswith("]"):
        return False
    try:
        json.loads(output)
        return True
    except json.JSONDecodeError:
        return False


def get_output_from_binary(result: TestResult) -> Optional[List[Dict]]:
    """Get output from compiled binary and parse it"""
    binary_file = os.path.join(COMPILED_DIR, f"iter_{result.iteration}_bin")
    if not os.path.exists(binary_file):
        return None

    with open(result.input_file, "r", encoding="utf-8") as f:
        input_data = f.read()

    try:
        run_result = subprocess.run(
            [binary_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=15
        )
        if run_result.returncode == 0:
            try:
                return json.loads(run_result.stdout)
            except json.JSONDecodeError:
                return None
    except Exception:
        pass
    return None


def compile_and_run(cpp_code: str, input_file: str, iteration: int) -> TestResult:
    result = TestResult()
    result.input_file = input_file
    result.iteration = iteration
    result.algorithm_code = cpp_code
    result.details["code_size"] = len(cpp_code)

    # Validate code structure before compilation
    validation_error = validate_code_structure(cpp_code)
    if validation_error:
        result.errors = f"Validation error: {validation_error}"
        return result

    try:
        # Prepare file names
        binary_file = os.path.join(COMPILED_DIR, f"iter_{iteration}_bin")

        # Save C++ code
        with open(CPP_SOURCE, "w", encoding="utf-8") as f:
            f.write(cpp_code)

        # Compile with optimizations
        compile_start = time.time()
        compile_result = subprocess.run(
            [CPP_COMPILER, "-std=c++17", "-O2", CPP_SOURCE,
             "-o", binary_file],
            capture_output=True,
            text=True
        )
        result.details["compile_time"] = time.time() - compile_start

        if compile_result.returncode != 0:
            result.errors = f"COMPILE ERROR:\n{compile_result.stderr}"
            return result

        result.compile_success = True

        # Get binary size
        if os.path.exists(binary_file):
            result.details["binary_size"] = os.path.getsize(binary_file)

        # Run with input data
        with open(input_file, "r", encoding="utf-8") as f:
            input_data = f.read()

        run_start = time.time()
        run_result = subprocess.run(
            [binary_file],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=15
        )
        result.execution_time = time.time() - run_start

        if run_result.returncode != 0:
            result.errors = f"RUNTIME ERROR ({run_result.returncode}):\n{run_result.stderr}"
            return result

        # Validate JSON structure
        if not validate_json_output(run_result.stdout):
            result.errors = f"INVALID OUTPUT: Not a valid JSON array\n{run_result.stdout[:200]}..."
            return result

        # Parse and validate output
        try:
            input_points = json.loads(input_data)
            output_points = json.loads(run_result.stdout)

            correction_quality, analysis = analyze_results(input_points, output_points)
            result.anomaly_detected = input_points != output_points
            result.correction_success = correction_quality
            result.details.update(analysis)

            # Save artifacts on success
            if result.correction_success:
                save_iteration_artifacts(iteration, cpp_code, binary_file)
                save_corrected_data(input_file, iteration, output_points)

        except json.JSONDecodeError as e:
            result.errors = f"JSON PARSE ERROR: {str(e)}\nOutput: {run_result.stdout[:200]}..."
        except Exception as e:
            result.errors = f"ANALYSIS ERROR: {str(e)}"

    except subprocess.TimeoutExpired:
        result.errors = "Execution timed out (15s)"
    except Exception as e:
        result.errors = f"SYSTEM ERROR: {str(e)}"

    return result


def get_ai_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=5000
    )
    return sanitize_code(response.choices[0].message.content)


def save_iteration_result(result: TestResult):
    """Save detailed results for each iteration"""
    filename = os.path.join(RESULTS_DIR,
                            f"iter_{result.iteration}_{result.input_file.replace('.', '_')}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result.__dict__, f, indent=2)


def generate_final_report(results: List[TestResult]):
    """Generate detailed final report with statistics"""
    successful_results = [r for r in results if r.correction_success]

    report = {
        "summary": {
            "total_iterations": len(results),
            "successful_runs": len(successful_results),
            "best_iteration": None,
            "best_execution_time": float('inf'),
            "initial_execution_time": None
        },
        "iterations": []
    }

    if successful_results:
        best_result = min(successful_results, key=lambda x: x.execution_time)
        report["summary"]["best_iteration"] = best_result.iteration
        report["summary"]["best_execution_time"] = best_result.execution_time
        report["summary"]["initial_execution_time"] = successful_results[0].execution_time

    for result in results:
        report["iterations"].append({
            "iteration": result.iteration,
            "timestamp": result.timestamp,
            "input_file": result.input_file,
            "compile_success": result.compile_success,
            "correction_success": result.correction_success,
            "execution_time": result.execution_time,
            "code_size": result.details["code_size"],
            "binary_size": result.details["binary_size"],
            "test_cases_passed": result.details.get("test_cases_passed", 0),
            "unchanged_points": result.details.get("unchanged_points", 0),
            "changed_points": result.details.get("changed_points", 0),
            "time_mismatches": result.details.get("time_mismatches", 0),
            "errors": result.errors
        })

    with open(os.path.join(RESULTS_DIR, "final_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n=== FINAL REPORT ===")
    print(f"Total iterations completed: {report['summary']['total_iterations']}")
    print(f"Successful runs: {report['summary']['successful_runs']}")

    if report["summary"]["best_iteration"] is not None:
        print(f"\nBest Algorithm (Iteration {report['summary']['best_iteration']}):")
        print(f"- Execution Time: {report['summary']['best_execution_time']:.4f}s")

        # Save best version
        best_code = os.path.join(RESULTS_DIR, f"iteration_{report['summary']['best_iteration']}_code.cpp")
        if os.path.exists(best_code):
            shutil.copy2(best_code, "best_algorithm.cpp")
            print(f"- Code saved to: best_algorithm.cpp")


def main():
    clean_environment()
    results = []
    prompt = generate_initial_prompt()
    feedback = "Initial version - no previous results"

    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} ---")

        # Get AI-generated code
        print("Generating algorithm...")
        try:
            cpp_code = get_ai_response(prompt)
            if len(cpp_code) > MAX_CODE_LENGTH:
                cpp_code = cpp_code[:MAX_CODE_LENGTH]
        except Exception as e:
            print(f"AI Error: {str(e)}")
            continue

        # Test with all input files
        iteration_results = []
        execution_stats = {
            "total": len(INPUT_FILES),
            "passed": 0,
            "avg_time": 0,
            "best_time": float('inf')
        }

        for input_file in INPUT_FILES:
            print(f"Testing with {input_file}...")
            result = compile_and_run(cpp_code, input_file, iteration)
            iteration_results.append(result)
            save_iteration_result(result)

            if result.correction_success:
                execution_stats["passed"] += 1
                execution_stats["avg_time"] += result.execution_time
                if result.execution_time < execution_stats["best_time"]:
                    execution_stats["best_time"] = result.execution_time

            if result.errors:
                print(f"Test failed: {result.errors[:200]}")

        # Calculate averages
        if execution_stats["passed"] > 0:
            execution_stats["avg_time"] /= execution_stats["passed"]

        # Store best result
        successful_results = [r for r in iteration_results if r.correction_success]
        if successful_results:
            best_iteration_result = min(successful_results, key=lambda x: x.execution_time)
            results.append(best_iteration_result)

        # Check completion condition
        if len([r for r in results if r.correction_success]) >= MAX_ITERATIONS:
            break

        # Prepare feedback for next iteration
        errors = "\n".join(r.errors for r in iteration_results if r.errors)
        feedback = (f"Iteration {iteration} Results:\n"
                    f"- Success Rate: {execution_stats['passed']}/{execution_stats['total']}\n"
                    f"- Avg Time: {execution_stats['avg_time']:.2f}s\n"
                    f"- Best Time: {execution_stats['best_time']:.2f}s\n"
                    f"- Main Issues: {errors[:500] or 'None'}")

        prompt = generate_improvement_prompt(cpp_code, errors, execution_stats, feedback)

    generate_final_report(results)


if __name__ == "__main__":
    main()