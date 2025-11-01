#pragma once

#include "VectorMath.h"
#include <vector>
#include <cmath>
#include <random>

class VerletPoint {
public:
    Vec2 CurrentPosition;
    Vec2 PreviousPosition;

    bool FixedPoint;
    float Boyancy = -15000.0f;
    float VelocityDamping = 0.75f;
    float VelocityMaximum = 10.0f;

    VerletPoint(Vec2 StartPosition, bool FixedPoint);

    void Update(float DeltaTime);
    void ApplyMouseCollision(bool MouseClicking, Vec2 MousePosition, float MouseRadius);
    void ContrainPosition(Vec2 CorrectionVector, bool MouseClicking, Vec2 MousePosition, float MouseRadius);
};

class VerletChain {
public:
    int NumberDisplayPointsPerSegment;
    int NumberDisplayPoints;
    int NumberPoints;
    float DesiredDistancePoints;

    std::vector<Vec2> SegmentCurvePoints;
    std::vector<int> SegmentWidths;
    std::vector<float> SegmentColorMultipliers;
    std::vector<VerletPoint> VerletPoints;

    VerletChain(Vec2 Position, int NumberPoints, float DesiredDistancePoints, int NumberDisplayPointsPerSegment = 0);

    std::vector<VerletPoint> GenerateChainPoints(Vec2 Position);
    void Update(float DeltaTime, bool MouseClicking, Vec2 MousePosition, float MouseRadius);

    void InitializeKelpVisuals();
    Vec2 Lerp(const Vec2& StartPoint, const Vec2& EndPoint, float Interpolator) const;
    Vec2 QuadraticBezier(const Vec2& StartPoint, const Vec2& CurvePoint, const Vec2& EndPoint, float Interpolator) const;
    std::vector<Vec2> CalculateDisplayPoints() const;
};
