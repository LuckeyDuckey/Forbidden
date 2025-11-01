#pragma once

#include <iostream>
#include <stdexcept>
#include <cmath>
#include <vector>

class Vec2 {
public:
    double x, y;

    // Constructors
    Vec2();
    Vec2(double scalar);
    Vec2(double x, double y);
    Vec2(const std::vector<double>& vec);
    
    // Copy and assignment
    Vec2(const Vec2& other);
    Vec2& operator=(const Vec2& other);

    // Indexing operators
    double& operator[](int index);
    const double& operator[](int index) const;

    // Arithmetic operators
    Vec2 operator+(const Vec2& other) const;
    Vec2 operator+(double scalar) const;
    Vec2 operator-(const Vec2& other) const;
    Vec2 operator-(double scalar) const;
    Vec2 operator*(const Vec2& other) const;
    Vec2 operator*(double scalar) const;
    Vec2 operator/(const Vec2& other) const;
    Vec2 operator/(double scalar) const;
    Vec2 operator%(const Vec2& other) const;
    Vec2 operator%(double scalar) const;
    
    // Unary operator
    Vec2 operator-() const;
    
    // In place operators
    Vec2& operator+=(const Vec2& other);
    Vec2& operator+=(double scalar);
    Vec2& operator-=(const Vec2& other);
    Vec2& operator-=(double scalar);
    Vec2& operator*=(const Vec2& other);
    Vec2& operator*=(double scalar);
    Vec2& operator/=(const Vec2& other);
    Vec2& operator/=(double scalar);
    Vec2& operator%=(const Vec2& other);
    Vec2& operator%=(double scalar);

    // Friend operators for scalar operations (scalar operator Vec2)
    friend Vec2 operator+(double scalar, const Vec2& vec);
    friend Vec2 operator-(double scalar, const Vec2& vec);
    friend Vec2 operator*(double scalar, const Vec2& vec);
    friend Vec2 operator/(double scalar, const Vec2& vec);

    // Utility methods
    Vec2 copy() const;
    Vec2& Clamp(const Vec2& minValue, const Vec2& maxValue);
    Vec2& Clamp(double minValue, double maxValue);
    double Length() const;
    Vec2 Normalize() const;
    double DistanceTo(const Vec2& other) const;
    double Dot(const Vec2& other) const;

    // Stream output
    friend std::ostream& operator<<(std::ostream& os, const Vec2& vec);
};