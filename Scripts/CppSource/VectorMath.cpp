#include "VectorMath.h"

#include <algorithm>

// Constructors
Vec2::Vec2() : x(0.0), y(0.0) {}

Vec2::Vec2(double scalar) : x(scalar), y(scalar) {}

Vec2::Vec2(double x, double y) : x(x), y(y) {}

Vec2::Vec2(const std::vector<double>& vec) {
    if (vec.size() != 2) {
        throw std::invalid_argument("Vec2 must be initialized with a vector of size 2");
    }
    x = vec[0];
    y = vec[1];
}

Vec2::Vec2(const Vec2& other) : x(other.x), y(other.y) {}

Vec2& Vec2::operator=(const Vec2& other) {
    if (this != &other) {
        x = other.x;
        y = other.y;
    }
    return *this;
}

// Indexing operators
double& Vec2::operator[](int index) {
    if (index == 0) return x;
    else if (index == 1) return y;
    else throw std::out_of_range("Vec2 index out of range");
}

const double& Vec2::operator[](int index) const {
    if (index == 0) return x;
    else if (index == 1) return y;
    else throw std::out_of_range("Vec2 index out of range");
}

// Arithmetic operators
Vec2 Vec2::operator+(const Vec2& other) const {
    return Vec2(x + other.x, y + other.y);
}

Vec2 Vec2::operator+(double scalar) const {
    return Vec2(x + scalar, y + scalar);
}

Vec2 Vec2::operator-(const Vec2& other) const {
    return Vec2(x - other.x, y - other.y);
}

Vec2 Vec2::operator-(double scalar) const {
    return Vec2(x - scalar, y - scalar);
}

Vec2 Vec2::operator*(const Vec2& other) const {
    return Vec2(x * other.x, y * other.y);
}

Vec2 Vec2::operator*(double scalar) const {
    return Vec2(x * scalar, y * scalar);
}

Vec2 Vec2::operator/(const Vec2& other) const {
    return Vec2(x / other.x, y / other.y);
}

Vec2 Vec2::operator/(double scalar) const {
    return Vec2(x / scalar, y / scalar);
}

Vec2 Vec2::operator%(const Vec2& other) const {
    return Vec2(std::fmod(x, other.x), std::fmod(y, other.y));
}

Vec2 Vec2::operator%(double scalar) const {
    return Vec2(std::fmod(x, scalar), std::fmod(y, scalar));
}

Vec2 Vec2::operator-() const {
    return Vec2(-x, -y);
}

// In-place operators
Vec2& Vec2::operator+=(const Vec2& other) {
    x += other.x;
    y += other.y;
    return *this;
}

Vec2& Vec2::operator+=(double scalar) {
    x += scalar;
    y += scalar;
    return *this;
}

Vec2& Vec2::operator-=(const Vec2& other) {
    x -= other.x;
    y -= other.y;
    return *this;
}

Vec2& Vec2::operator-=(double scalar) {
    x -= scalar;
    y -= scalar;
    return *this;
}

Vec2& Vec2::operator*=(const Vec2& other) {
    x *= other.x;
    y *= other.y;
    return *this;
}

Vec2& Vec2::operator*=(double scalar) {
    x *= scalar;
    y *= scalar;
    return *this;
}

Vec2& Vec2::operator/=(const Vec2& other) {
    x /= other.x;
    y /= other.y;
    return *this;
}

Vec2& Vec2::operator/=(double scalar) {
    x /= scalar;
    y /= scalar;
    return *this;
}

Vec2& Vec2::operator%=(const Vec2& other) {
    x = std::fmod(x, other.x);
    y = std::fmod(y, other.y);
    return *this;
}

Vec2& Vec2::operator%=(double scalar) {
    x = std::fmod(x, scalar);
    y = std::fmod(y, scalar);
    return *this;
}

// Friend operators for scalar operations
Vec2 operator+(double scalar, const Vec2& vec) {
    return Vec2(scalar + vec.x, scalar + vec.y);
}

Vec2 operator-(double scalar, const Vec2& vec) {
    return Vec2(scalar - vec.x, scalar - vec.y);
}

Vec2 operator*(double scalar, const Vec2& vec) {
    return Vec2(scalar * vec.x, scalar * vec.y);
}

Vec2 operator/(double scalar, const Vec2& vec) {
    return Vec2(scalar / vec.x, scalar / vec.y);
}

// Utility methods
Vec2 Vec2::copy() const {
    return Vec2(x, y);
}

Vec2& Vec2::Clamp(const Vec2& minValue, const Vec2& maxValue) {
    x = std::max(minValue.x, std::min(x, maxValue.x));
    y = std::max(minValue.y, std::min(y, maxValue.y));
    return *this;
}

Vec2& Vec2::Clamp(double minValue, double maxValue) {
    x = std::max(minValue, std::min(x, maxValue));
    y = std::max(minValue, std::min(y, maxValue));
    return *this;
}

double Vec2::Length() const {
    return std::sqrt(x * x + y * y);
}

Vec2 Vec2::Normalize() const {
    double length = Length();
    if (length == 0.0) {
        return Vec2(0.0, 0.0);
    }
    return Vec2(x / length, y / length);
}

double Vec2::DistanceTo(const Vec2& other) const {
    return Vec2(x - other.x, y - other.y).Length();
}

double Vec2::Dot(const Vec2& other) const {
    return x * other.x + y * other.y;
}

// Stream output
std::ostream& operator<<(std::ostream& os, const Vec2& vec) {
    os << "Vec2(" << vec.x << ", " << vec.y << ")";
    return os;
}