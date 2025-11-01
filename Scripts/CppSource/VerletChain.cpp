#include "VerletChain.h"

VerletPoint::VerletPoint(Vec2 StartPosition, bool FixedPoint) :
    CurrentPosition{StartPosition},
    PreviousPosition{StartPosition},
    FixedPoint{FixedPoint}
{}

void VerletPoint::Update(float DeltaTime) {
    if (FixedPoint) {
        return;
    }

    Vec2 Acceleration = 0.5f * Vec2(0.0f, Boyancy) * DeltaTime * DeltaTime;
    Vec2 Velocity = ((CurrentPosition - PreviousPosition) * VelocityDamping).Clamp(-VelocityMaximum, VelocityMaximum);

    PreviousPosition = CurrentPosition;
    CurrentPosition += Velocity + Acceleration;
}

void VerletPoint::ApplyMouseCollision(bool MouseClicking, Vec2 MousePosition, float MouseRadius) {
    if (!MouseClicking) {
        return;
    }

    // No collision return early
    float DistanceToMouse = MousePosition.DistanceTo(CurrentPosition);
    if (DistanceToMouse - MouseRadius >= 0) {
        return;
    }

    // Push point outside mouse collider
    Vec2 Direction = (CurrentPosition - MousePosition).Normalize();
    CurrentPosition = MousePosition + Direction * MouseRadius;
}

void VerletPoint::ContrainPosition(Vec2 CorrectionVector, bool MouseClicking, Vec2 MousePosition, float MouseRadius) {
    if (FixedPoint) {
        return;
    }

    CurrentPosition += CorrectionVector;
    ApplyMouseCollision(MouseClicking, MousePosition, MouseRadius);
}

//////////////////////////////
//       Verlet Chain       //
//////////////////////////////

VerletChain::VerletChain(Vec2 Position, int NumberPoints, float DesiredDistancePoints, int NumberDisplayPointsPerSegment) :
    NumberPoints{NumberPoints},
    DesiredDistancePoints{DesiredDistancePoints},
    NumberDisplayPointsPerSegment{NumberDisplayPointsPerSegment},
    NumberDisplayPoints{(NumberPoints - 1) * (NumberDisplayPointsPerSegment + 1) + 1},
    VerletPoints{GenerateChainPoints(Position)}
{
    InitializeKelpVisuals();
}

std::vector<VerletPoint> VerletChain::GenerateChainPoints(Vec2 Position) {
    std::vector<VerletPoint> Points;
    Points.reserve(NumberPoints);
    
    for (int Index = 0; Index < NumberPoints; ++Index) {
        // First node will be fixed
        Points.emplace_back(Position - Vec2(0.0f, DesiredDistancePoints * Index), (Index == 0));
    }
    
    return Points;
}

void VerletChain::Update(float DeltaTime, bool MouseClicking, Vec2 MousePosition, float MouseRadius) {
    // Start with velocity position updates
    for (auto& Point : VerletPoints) {
        Point.Update(DeltaTime);
    }
    
    // Next do the chain constraints
    for (int Iteration = 0; Iteration < round(NumberPoints * 50 * DeltaTime); ++Iteration) {
        for (int Index = 0; Index < NumberPoints - 1; ++Index) {
            VerletPoint& CurrentPoint = VerletPoints[Index];
            VerletPoint& NextPoint = VerletPoints[Index + 1];
            
            Vec2 PositionDifference = CurrentPoint.CurrentPosition - NextPoint.CurrentPosition;
            float DistancePointsError = DesiredDistancePoints - PositionDifference.Length();
            Vec2 CorrectionVector = PositionDifference.Normalize() * DistancePointsError * 0.5f;
            
            CurrentPoint.ContrainPosition(CorrectionVector, MouseClicking, MousePosition, MouseRadius);
            NextPoint.ContrainPosition(-CorrectionVector, MouseClicking, MousePosition, MouseRadius);
        }
    }
}

void VerletChain::InitializeKelpVisuals() {
    std::random_device RandomDevice;
    std::mt19937 Generator(RandomDevice());
    std::uniform_real_distribution<float> CurveDistribution(-10.0f, 10.0f);
    std::uniform_int_distribution<int> WidthDistribution(2, 4);
    std::uniform_real_distribution<float> ColorDistribution(0.75f, 1.0f);
    
    // Initialize curve points for each segment
    SegmentCurvePoints.reserve(NumberPoints - 1);
    for (int Index = 0; Index < NumberPoints - 1; ++Index) {
        SegmentCurvePoints.emplace_back(CurveDistribution(Generator), CurveDistribution(Generator));
    }
    
    // Initialize widths for each display point
    SegmentWidths.reserve(NumberDisplayPoints);
    for (int Index = 0; Index < NumberDisplayPoints; ++Index) {
        SegmentWidths.push_back(WidthDistribution(Generator));
    }
    
    // Initialize color multiplierss for each display point
    SegmentColorMultipliers.reserve(NumberDisplayPoints);
    for (int Index = 0; Index < NumberDisplayPoints; ++Index) {
        SegmentColorMultipliers.emplace_back(ColorDistribution(Generator));
    }
}

Vec2 VerletChain::Lerp(const Vec2& StartPoint, const Vec2& EndPoint, float Interpolator) const {
    return StartPoint + (EndPoint - StartPoint) * Interpolator;
}

Vec2 VerletChain::QuadraticBezier(const Vec2& StartPoint, const Vec2& CurvePoint, const Vec2& EndPoint, float Interpolator) const {
    Vec2 LerpStartToCurve = Lerp(StartPoint, CurvePoint, Interpolator);
    Vec2 LerpCurveToEnd = Lerp(CurvePoint, EndPoint, Interpolator);
    return Lerp(LerpStartToCurve, LerpCurveToEnd, Interpolator);
}

std::vector<Vec2> VerletChain::CalculateDisplayPoints() const {
    std::vector<Vec2> DisplayPoints;
    DisplayPoints.reserve(NumberDisplayPoints);
    
    for (int Index = 0; Index < NumberPoints - 1; ++Index) {
        const Vec2& CurrentPoint = VerletPoints[Index].CurrentPosition;
        const Vec2& NextPoint = VerletPoints[Index + 1].CurrentPosition;
        
        DisplayPoints.push_back(CurrentPoint);
        Vec2 CurvePoint = Lerp(CurrentPoint, NextPoint, 0.5f) + SegmentCurvePoints[Index];
        
        for (int Count = 0; Count < NumberDisplayPointsPerSegment; ++Count) {
            float Interpolator = static_cast<float>(Count + 1) / static_cast<float>(NumberDisplayPointsPerSegment + 1);
            DisplayPoints.push_back(QuadraticBezier(CurrentPoint, CurvePoint, NextPoint, Interpolator));
        }
    }
    
    DisplayPoints.push_back(VerletPoints[NumberPoints - 1].CurrentPosition);
    return DisplayPoints;
}
