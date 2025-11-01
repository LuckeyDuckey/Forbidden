#pragma once

#include "VectorMath.h"
#include <vector>
#include <random>
#include <cmath>
#include <limits>

class Boid {
public:
    Vec2 Position;
    Vec2 Direction;
    
    Vec2 BoundsMin;
    Vec2 BoundsMax;
    double BoundsMargin;
    
    double Speed;
    
    double AlignmentRadius;
    double CohesionRadius;
    double SeperationRadius;
    
    double AlignmentFactor;
    double CohesionFactor;
    double SeperationFactor;
    
    double TurnFactorRules;
    double TurnFactorCollisions;

    Boid(Vec2 BoundsMin, Vec2 BoundsMax, double BoundsMargin);
    
    Vec2 ApplyRules(const std::vector<Boid*>& Boids);
    Vec2 ApplyCollisions(bool MouseClicking, Vec2 MousePosition, float MouseRadius);
    Vec2 RayCircleIntersection(bool MouseClicking, Vec2 MousePosition, float MouseRadius);
    void Update(const std::vector<Boid*>& Boids, double DeltaTime, bool MouseClicking, Vec2 MousePosition, float MouseRadius);
};