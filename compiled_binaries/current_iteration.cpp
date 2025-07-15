
#define _USE_MATH_DEFINES
#include <iostream>
#include <vector>
#include <cmath>
#include <iomanip>
#include <string>
#include <sstream>
#include <stdexcept>
#include <limits>
#include <cctype>

struct Point {
    double lat;
    double lon;
    int time;
    bool anomalous = false;
};

double deg2rad(double deg) {
    return deg * M_PI / 180.0;
}

double haversine(double lat1, double lon1, double lat2, double lon2) {
    // Earth radius in meters
    const double R = 6371000.0;
    double dlat = deg2rad(lat2 - lat1);
    double dlon = deg2rad(lon2 - lon1);
    double a = sin(dlat/2) * sin(dlat/2) +
               cos(deg2rad(lat1)) * cos(deg2rad(lat2)) *
               sin(dlon/2) * sin(dlon/2);
    double c = 2 * atan2(sqrt(a), sqrt(1-a));
    return R * c;
}

// Minimal JSON parser for array of objects [{"lat":123,"lon":456,"time":789},...]
bool parse_json_array(const std::string& input, std::vector<Point>& points) {
    size_t i = 0;
    while (i < input.size() && std::isspace(input[i])) ++i;
    if (i >= input.size() || input[i] != '[') return false;
    ++i;
    while (i < input.size()) {
        while (i < input.size() && std::isspace(input[i])) ++i;
        if (i < input.size() && input[i] == ']') {
            ++i;
            break;
        }
        if (i >= input.size() || input[i] != '{') return false;
        ++i;
        double lat = std::numeric_limits<double>::quiet_NaN();
        double lon = std::numeric_limits<double>::quiet_NaN();
        int time = 0;
        bool lat_set = false, lon_set = false, time_set = false;
        while (i < input.size()) {
            while (i < input.size() && std::isspace(input[i])) ++i;
            if (i < input.size() && input[i] == '}') {
                ++i;
                break;
            }
            // Parse key
            if (i >= input.size() || input[i] != '"') return false;
            ++i;
            size_t key_start = i;
            while (i < input.size() && input[i] != '"') ++i;
            if (i >= input.size()) return false;
            std::string key = input.substr(key_start, i - key_start);
            ++i;
            while (i < input.size() && std::isspace(input[i])) ++i;
            if (i >= input.size() || input[i] != ':') return false;
            ++i;
            while (i < input.size() && std::isspace(input[i])) ++i;
            // Parse value
            size_t val_start = i;
            if (key == "lat" || key == "lon") {
                bool neg = false;
                if (i < input.size() && input[i] == '-') { neg = true; ++i; }
                double val = 0.0;
                bool has_dot = false;
                double frac = 0.1;
                while (i < input.size() && (std::isdigit(input[i]) || input[i] == '.')) {
                    if (input[i] == '.') {
                        if (has_dot) return false;
                        has_dot = true;
                        ++i;
                        continue;
                    }
                    if (!has_dot) {
                        val = val * 10 + (input[i] - '0');
                    } else {
                        val += (input[i] - '0') * frac;
                        frac *= 0.1;
                    }
                    ++i;
                }
                if (neg) val = -val;
                if (key == "lat") { lat = val; lat_set = true; }
                else { lon = val; lon_set = true; }
            } else if (key == "time") {
                bool neg = false;
                if (i < input.size() && input[i] == '-') { neg = true; ++i; }
                int val = 0;
                while (i < input.size() && std::isdigit(input[i])) {
                    val = val * 10 + (input[i] - '0');
                    ++i;
                }
                if (neg) val = -val;
                time = val;
                time_set = true;
            } else {
                return false;
            }
            while (i < input.size() && std::isspace(input[i])) ++i;
            if (i < input.size() && input[i] == ',') ++i;
        }
        if (!lat_set || !lon_set || !time_set) return false;
        points.push_back(Point{lat, lon, time});
        while (i < input.size() && std::isspace(input[i])) ++i;
        if (i < input.size() && input[i] == ',') ++i;
    }
    while (i < input.size() && std::isspace(input[i])) ++i;
    return i == input.size();
}

void print_json_array(const std::vector<Point>& points) {
    std::cout << '[';
    for (size_t i = 0; i < points.size(); ++i) {
        if (i) std::cout << ',';
        std::cout << "{\"lat\":";
        std::cout << std::fixed << std::setprecision(8) << points[i].lat;
        std::cout << ",\"lon\":";
        std::cout << std::fixed << std::setprecision(8) << points[i].lon;
        std::cout << ",\"time\":";
        std::cout << points[i].time;
        std::cout << '}';
    }
    std::cout << ']' << std::endl;
}

void detect_anomalies(std::vector<Point>& points) {
    const double SPEED_THRESHOLD = 50.0; // m/s
    size_t n = points.size();
    if (n < 3) return;
    // Never change first or last point
    for (size_t i = 1; i + 1 < n; ++i) {
        double dist_prev = haversine(points[i-1].lat, points[i-1].lon, points[i].lat, points[i].lon);
        double dt_prev = points[i].time - points[i-1].time;
        double speed_prev = (dt_prev > 0) ? dist_prev / dt_prev : 0.0;
        double dist_next = haversine(points[i].lat, points[i].lon, points[i+1].lat, points[i+1].lon);
        double dt_next = points[i+1].time - points[i].time;
        double speed_next = (dt_next > 0) ? dist_next / dt_next : 0.0;
        if (speed_prev > SPEED_THRESHOLD || speed_next > SPEED_THRESHOLD) {
            points[i].anomalous = true;
        }
    }
}

void correct_anomalies(std::vector<Point>& points) {
    size_t n = points.size();
    if (n < 3) return;
    for (size_t i = 1; i + 1 < n; ++i) {
        if (points[i].anomalous) {
            // Use linear interpolation between neighbors
            double frac = double(points[i].time - points[i-1].time) /
                          double(points[i+1].time - points[i-1].time);
            if (frac < 0.0) frac = 0.0;
            if (frac > 1.0) frac = 1.0;
            points[i].lat = points[i-1].lat + (points[i+1].lat - points[i-1].lat) * frac;
            points[i].lon = points[i-1].lon + (points[i+1].lon - points[i-1].lon) * frac;
        }
    }
}

int main() {
    std::ios::sync_with_stdio(false);
    std::cin.tie(nullptr);
    // Read all stdin
    std::string input, line;
    while (std::getline(std::cin, line)) {
        input += line;
    }
    std::vector<Point> points;
    try {
        if (!parse_json_array(input, points)) {
            std::cerr << "Invalid JSON input\n";
            return 1;
        }
    } catch (...) {
        std::cerr << "Error parsing input\n";
        return 1;
    }
    if (points.empty()) {
        std::cerr << "Empty input\n";
        return 1;
    }
    try {
        detect_anomalies(points);
        correct_anomalies(points);
        print_json_array(points);
    } catch (...) {
        std::cerr << "Error during processing\n";
        return 1;
    }
    return 0;
}
