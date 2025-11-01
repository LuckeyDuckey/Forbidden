#include "Boid.h"

static std::random_device RandomDevice;
static std::mt19937 Generator(RandomDevice());

Boid::Boid(Vec2 BoundsMin, Vec2 BoundsMax, double BoundsMargin)
    : BoundsMin(BoundsMin), BoundsMax(BoundsMax), BoundsMargin(BoundsMargin)
{
    std::uniform_real_distribution<> WidthDistribution(BoundsMin.x, BoundsMax.x);
    std::uniform_real_distribution<> HeightDistribution(BoundsMin.y, BoundsMax.y);
    std::uniform_real_distribution<> DirectionDistribution(-1.0, 1.0);
    
    Position = Vec2(WidthDistribution(Generator), HeightDistribution(Generator));
    Direction = Vec2(DirectionDistribution(Generator), DirectionDistribution(Generator)).Normalize();
    
    Speed = 175.0;
    
    AlignmentRadius = 100.0;
    CohesionRadius = 100.0;
    SeperationRadius = 75.0;
    
    AlignmentFactor = 0.75;
    CohesionFactor = 1.0;
    SeperationFactor = 0.95;
    
    TurnFactorRules = 5.0;
    TurnFactorCollisions = 15.0;
}

Vec2 Boid::ApplyRules(const std::vector<Boid*>& Boids) {
    Vec2 SeperationDirection(0, 0);
    int SeperationCount = 0;
    
    Vec2 CohesionDirection(0, 0);
    int CohesionCount = 0;
    
    Vec2 AlignmentDirection = Direction;
    int AlignmentCount = 1;
    
    for (Boid* Boid : Boids) {
        if (Boid == this) {
            continue;
        }
        
        double distance = Position.DistanceTo(Boid->Position);
        
        if (distance < SeperationRadius) {
            SeperationDirection = SeperationDirection + (Boid->Position - Position).Normalize();
            SeperationCount++;
        }
        
        if (distance < CohesionRadius) {
            CohesionDirection = CohesionDirection + Boid->Position;
            CohesionCount++;
        }
        
        if (distance < AlignmentRadius) {
            AlignmentDirection = AlignmentDirection + Boid->Direction;
            AlignmentCount++;
        }
    }
    
    if (SeperationCount > 0) {
        SeperationDirection = (SeperationDirection / static_cast<double>(SeperationCount)).Normalize() * (-SeperationFactor);
    }
    
    if (CohesionCount > 0) {
        CohesionDirection = ((CohesionDirection / static_cast<double>(CohesionCount)) - Position).Normalize() * CohesionFactor;
    }
    
    if (AlignmentCount > 0) {
        AlignmentDirection = (AlignmentDirection / static_cast<double>(AlignmentCount)).Normalize() * AlignmentFactor;
    }
    
    return (AlignmentDirection + CohesionDirection + SeperationDirection).Normalize();
}

Vec2 Boid::RayCircleIntersection(bool MouseClicking, Vec2 MousePosition, float MouseRadius) {
    Vec2 CircleToPosition = Position - MousePosition;
    
    double A = Direction.Dot(Direction);
    double B = 2.0 * CircleToPosition.Dot(Direction);
    double C = CircleToPosition.Dot(CircleToPosition) - MouseRadius * MouseRadius;
    
    double Discriminant = B * B - 4.0 * A * C;
    if (Discriminant < 0) {
        return Vec2(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
    }
    
    double DiscriminantSqrt = std::sqrt(Discriminant);
    double IntersectionNear = (-B - DiscriminantSqrt) * 0.5;
    double IntersectionFar = (-B + DiscriminantSqrt) * 0.5;
    
    double IntersectionDistance = std::numeric_limits<double>::quiet_NaN();
    
    if (IntersectionNear >= 0 && IntersectionFar >= 0) {
        IntersectionDistance = std::min(IntersectionNear, IntersectionFar);
    } else if (IntersectionNear >= 0) {
        IntersectionDistance = IntersectionNear;
    } else if (IntersectionFar >= 0) {
        IntersectionDistance = IntersectionFar;
    }
    
    if (std::isnan(IntersectionDistance)) {
        return Vec2(std::numeric_limits<double>::quiet_NaN(), std::numeric_limits<double>::quiet_NaN());
    }
    
    return Position + Direction * IntersectionDistance;
}

Vec2 Boid::ApplyCollisions(bool MouseClicking, Vec2 MousePosition, float MouseRadius) {
    // Wrap horizontally
    if (Position.x < BoundsMin.x - BoundsMargin) {
        Position.x = BoundsMax.x + BoundsMargin;
    }
    if (Position.x > BoundsMax.x + BoundsMargin) {
        Position.x = BoundsMin.x - BoundsMargin;
    }
    
    // Bounce vertically
    if (Position.y < BoundsMin.y + BoundsMargin) {
        return Vec2(0, 1);
    }
    if (Position.y > BoundsMax.y - BoundsMargin) {
        return Vec2(0, -1);
    }
    
    if (!MouseClicking) {
        return Vec2(0, 0);
    }
    
    // If inside mouse circle, flee
    Vec2 CircleToPosition = Position - MousePosition;
    if (CircleToPosition.Length() < MouseRadius) {
        return CircleToPosition.Normalize();
    }
    
    // If going to hit mouse circle, steer away
    Vec2 IntersectionPosition = RayCircleIntersection(MouseClicking, MousePosition, MouseRadius);
    if (!std::isnan(IntersectionPosition.x) && Position.DistanceTo(IntersectionPosition) < BoundsMargin) {
        return (IntersectionPosition - MousePosition).Normalize();
    }
    
    return Vec2(0, 0);
}

void Boid::Update(const std::vector<Boid*>& Boids, double DeltaTime, bool MouseClicking, Vec2 MousePosition, float MouseRadius) {
    Vec2 DesiredDirectionRules = ApplyRules(Boids) * TurnFactorRules;
    Vec2 DesiredDirectionCollisions = ApplyCollisions(MouseClicking, MousePosition, MouseRadius) * TurnFactorCollisions;
    
    Vec2 DesiredDirection = DesiredDirectionCollisions.Length() > 0 
        ? DesiredDirectionCollisions 
        : DesiredDirectionRules;
    
    Direction = Direction + (DesiredDirection - Direction) * DeltaTime;
    Direction = Direction.Normalize();
    
    Position = Position + Direction * Speed * DeltaTime;
}
