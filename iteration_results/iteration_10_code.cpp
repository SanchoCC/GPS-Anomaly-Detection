
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

// Simple JSON parsing utilities (no external dependencies)
struct GPSPoint {
    int lat;
    int lon;
    int time;
};

bool is_digit_or_minus(char c) {
    return std::isdigit(c) || c == '-';
}

// Parse a single integer value from a JSON string at the given position
bool parse_int(const std::string& s, size_t& pos, int& value) {
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    bool neg = false;
    if (pos < s.size() && s[pos] == '-') {
        neg = true;
        ++pos;
    }
    if (pos >= s.size() || !std::isdigit(s[pos])) return false;
    int v = 0;
    while (pos < s.size() && std::isdigit(s[pos])) {
        v = v * 10 + (s[pos] - '0');
        ++pos;
    }
    value = neg ? -v : v;
    return true;
}

// Parse a key in the form of "key":
bool parse_key(const std::string& s, size_t& pos, std::string& key) {
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    if (pos >= s.size() || s[pos] != '"') return false;
    ++pos;
    size_t start = pos;
    while (pos < s.size() && s[pos] != '"') ++pos;
    if (pos >= s.size()) return false;
    key = s.substr(start, pos - start);
    ++pos;
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    if (pos >= s.size() || s[pos] != ':') return false;
    ++pos;
    return true;
}

// Parse a single GPSPoint object from a JSON string at the given position
bool parse_gps_point(const std::string& s, size_t& pos, GPSPoint& pt) {
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    if (pos >= s.size() || s[pos] != '{') return false;
    ++pos;
    bool lat_set = false, lon_set = false, time_set = false;
    for (int i = 0; i < 3; ++i) {
        std::string key;
        if (!parse_key(s, pos, key)) return false;
        int value;
        if (!parse_int(s, pos, value)) return false;
        if (key == "lat") {
            pt.lat = value;
            lat_set = true;
        } else if (key == "lon") {
            pt.lon = value;
            lon_set = true;
        } else if (key == "time") {
            pt.time = value;
            time_set = true;
        } else {
            return false;
        }
        while (pos < s.size() && std::isspace(s[pos])) ++pos;
        if (i < 2) {
            if (pos >= s.size() || s[pos] != ',') return false;
            ++pos;
        }
    }
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    if (pos >= s.size() || s[pos] != '}') return false;
    ++pos;
    return lat_set && lon_set && time_set;
}

// Parse the full JSON array of GPS points
bool parse_gps_array(const std::string& s, std::vector<GPSPoint>& points) {
    size_t pos = 0;
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    if (pos >= s.size() || s[pos] != '[') return false;
    ++pos;
    while (true) {
        while (pos < s.size() && std::isspace(s[pos])) ++pos;
        if (pos < s.size() && s[pos] == ']') {
            ++pos;
            break;
        }
        GPSPoint pt;
        if (!parse_gps_point(s, pos, pt)) return false;
        points.push_back(pt);
        while (pos < s.size() && std::isspace(s[pos])) ++pos;
        if (pos < s.size() && s[pos] == ',') {
            ++pos;
            continue;
        }
        if (pos < s.size() && s[pos] == ']') {
            ++pos;
            break;
        }
    }
    while (pos < s.size() && std::isspace(s[pos])) ++pos;
    return pos == s.size();
}

// Haversine formula to compute distance in meters between two lat/lon points (integers in microdegrees)
double haversine(int lat1, int lon1, int lat2, int lon2) {
    // Convert to degrees
    double dlat = (lat2 - lat1) * 1e-6;
    double dlon = (lon2 - lon1) * 1e-6;
    double alat1 = lat1 * 1e-6 * M_PI / 180.0;
    double alat2 = lat2 * 1e-6 * M_PI / 180.0;
    double dlat_rad = dlat * M_PI / 180.0;
    double dlon_rad = dlon * M_PI / 180.0;
    double a = std::sin(dlat_rad/2) * std::sin(dlat_rad/2) +
               std::cos(alat1) * std::cos(alat2) *
               std::sin(dlon_rad/2) * std::sin(dlon_rad/2);
    double c = 2 * std::atan2(std::sqrt(a), std::sqrt(1-a));
    return 6371000.0 * c;
}

// Detect anomalies: speed > 50 m/s between consecutive points
std::vector<bool> detect_anomalies(const std::vector<GPSPoint>& points) {
    size_t n = points.size();
    std::vector<bool> is_anomaly(n, false);
    for (size_t i = 1; i < n; ++i) {
        int dt = points[i].time - points[i-1].time;
        if (dt <= 0) continue; // skip invalid time
        double dist = haversine(points[i-1].lat, points[i-1].lon, points[i].lat, points[i].lon);
        double speed = dist / dt;
        if (speed > 50.0) {
            is_anomaly[i] = true;
        }
    }
    for (size_t i = 0; i + 1 < n; ++i) {
        int dt = points[i+1].time - points[i].time;
        if (dt <= 0) continue;
        double dist = haversine(points[i].lat, points[i].lon, points[i+1].lat, points[i+1].lon);
        double speed = dist / dt;
        if (speed > 50.0) {
            is_anomaly[i] = true;
        }
    }
    is_anomaly[0] = false;
    if (n > 0) is_anomaly[n-1] = false;
    return is_anomaly;
}

// Interpolate anomalous points using linear interpolation between previous and next non-anomalous points
void correct_anomalies(std::vector<GPSPoint>& points, const std::vector<bool>& is_anomaly) {
    size_t n = points.size();
    if (n < 3) return;
    for (size_t i = 1; i + 1 < n; ++i) {
        if (!is_anomaly[i]) continue;
        // Find previous non-anomalous
        size_t prev = i-1;
        while (prev > 0 && is_anomaly[prev]) --prev;
        // Find next non-anomalous
        size_t next = i+1;
        while (next + 1 < n && is_anomaly[next]) ++next;
        if (is_anomaly[prev] || is_anomaly[next]) continue; // can't interpolate
        int t0 = points[prev].time, t1 = points[next].time, t = points[i].time;
        if (t1 == t0) continue;
        double alpha = double(t - t0) / (t1 - t0);
        int new_lat = int(std::round(points[prev].lat + alpha * (points[next].lat - points[prev].lat)));
        int new_lon = int(std::round(points[prev].lon + alpha * (points[next].lon - points[prev].lon)));
        points[i].lat = new_lat;
        points[i].lon = new_lon;
        // time remains unchanged
    }
}

// Output JSON array in required format
void output_json(const std::vector<GPSPoint>& points) {
    std::cout << "[";
    for (size_t i = 0; i < points.size(); ++i) {
        if (i) std::cout << ",";
        std::cout << "{\"lat\":" << points[i].lat
                  << ",\"lon\":" << points[i].lon
                  << ",\"time\":" << points[i].time << "}";
    }
    std::cout << "]\n";
}

int main() {
    // Read all input from stdin
    std::string input, line;
    while (std::getline(std::cin, line)) {
        input += line;
    }
    std::vector<GPSPoint> points;
    try {
        if (!parse_gps_array(input, points)) {
            std::cerr << "Invalid JSON input\n";
            return 1;
        }
        if (points.size() < 2) {
            output_json(points);
            return 0;
        }
        std::vector<bool> is_anomaly = detect_anomalies(points);
        correct_anomalies(points, is_anomaly);
        output_json(points);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
