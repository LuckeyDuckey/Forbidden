#include <pybind11/pybind11.h>
#include <pybind11/operators.h>
#include <pybind11/stl.h>

#include "VectorMath.h"
#include "VerletChain.h"
#include "Boid.h"

namespace Python = pybind11;

PYBIND11_MODULE(Simulations, ModuleObject) {
    Python::class_<Vec2>(ModuleObject, "Vec2")
        // Constructors
        .def(Python::init<>())
        .def(Python::init<double>())
        .def(Python::init<double, double>())
        .def(Python::init<const std::vector<double>&>())
        
        // Properties
        .def_readwrite("x", &Vec2::x)
        .def_readwrite("y", &Vec2::y)
        
        // Indexing (allows for vec[0], vec[1])
        .def("__getitem__", [](const Vec2& v, int i) {
            if (i < 0 || i > 1) throw Python::index_error("Vec2 index out of range");
            return v[i];
        })
        .def("__setitem__", [](Vec2& v, int i, double value) {
            if (i < 0 || i > 1) throw Python::index_error("Vec2 index out of range");
            v[i] = value;
        })
        
        // Make it iterable
        .def("__iter__", [](const Vec2& v) {
            return Python::make_iterator(&v.x, &v.x + 2);
        }, Python::keep_alive<0, 1>())
        
        // Length support
        .def("__len__", [](const Vec2& v) { return 2; })
        
        // Arithmetic operators
        .def(Python::self + Python::self) // Vec2 + Vec2
        .def(Python::self + double())     // Vec2 + scalar
        .def(double() + Python::self)     // scalar + Vec2
        .def(Python::self - Python::self) // Vec2 - Vec2
        .def(Python::self - double())     // Vec2 - scalar
        .def(double() - Python::self)     // scalar - Vec2
        .def(Python::self * Python::self) // Vec2 * Vec2
        .def(Python::self * double())     // Vec2 * scalar
        .def(double() * Python::self)     // scalar * Vec2
        .def(Python::self / Python::self) // Vec2 / Vec2
        .def(Python::self / double())     // Vec2 / scalar
        .def(double() / Python::self)     // scalar / Vec2
        .def(Python::self % Python::self) // Vec2 % Vec2
        .def(Python::self % double())     // Vec2 % scalar
        .def(-Python::self)               // -Vec2
        
        // In place operators
        .def(Python::self += Python::self) // Vec2 += Vec2
        .def(Python::self += double())     // Vec2 += scalar
        .def(Python::self -= Python::self) // Vec2 -= Vec2
        .def(Python::self -= double())     // Vec2 -= scalar
        .def(Python::self *= Python::self) // Vec2 *= Vec2
        .def(Python::self *= double())     // Vec2 *= scalar
        .def(Python::self /= Python::self) // Vec2 /= Vec2
        .def(Python::self /= double())     // Vec2 /= scalar
        .def(Python::self %= Python::self) // Vec2 %= Vec2
        .def(Python::self %= double())     // Vec2 %= scalar
        
        // Utility methods
        .def("copy", &Vec2::copy, "Return a copy of the vector")
        .def("Clamp", Python::overload_cast<const Vec2&, const Vec2&>(&Vec2::Clamp), 
             "Clamp vector components between min and max vectors", Python::return_value_policy::reference_internal)
        .def("Clamp", Python::overload_cast<double, double>(&Vec2::Clamp), 
             "Clamp vector components between min and max scalars", Python::return_value_policy::reference_internal)
        .def("Length", &Vec2::Length, "Return the length (magnitude) of the vector")
        .def("Normalize", &Vec2::Normalize, "Return a normalized version of the vector")
        .def("DistanceTo", &Vec2::DistanceTo, "Return the distance to another vector")
        .def("Dot", &Vec2::Dot, "Return the dot product with another vector")
        
        // String representation
        .def("__repr__", [](const Vec2& Vector) {
            return "Vec2(" + std::to_string(Vector.x) + ", " + std::to_string(Vector.y) + ")";
        })
        .def("__str__", [](const Vec2& Vector) {
            return "Vec2(" + std::to_string(Vector.x) + ", " + std::to_string(Vector.y) + ")";
        });

    Python::class_<VerletChain>(ModuleObject, "VerletChain")
        .def(Python::init<Vec2, int, float, int>(),
            Python::arg("Position"),
            Python::arg("NumberPoints"),
            Python::arg("DesiredDistancePoints"),
            Python::arg("NumberDisplayPointsPerSegment"))
        .def("Update", &VerletChain::Update,
            Python::arg("DeltaTime"),
            Python::arg("MouseClicking"),
            Python::arg("MousePosition"),
            Python::arg("MouseRadius"))
        .def("CalculateDisplayPoints", &VerletChain::CalculateDisplayPoints)
        .def_readwrite("SegmentWidths", &VerletChain::SegmentWidths)
        .def_readwrite("SegmentColorMultipliers", &VerletChain::SegmentColorMultipliers);

    Python::class_<Boid>(ModuleObject, "Boid")
        .def(Python::init<Vec2, Vec2, double>(),
            Python::arg("BoundsMin"),
            Python::arg("BoundsMax"),
            Python::arg("BoundsMargin"))
        .def("Update", &Boid::Update,
            Python::arg("Boids"),
            Python::arg("DeltaTime"),
            Python::arg("MouseClicking"),
            Python::arg("MousePosition"),
            Python::arg("MouseRadius"))
        .def_readwrite("Position", &Boid::Position)
        .def_readwrite("Direction", &Boid::Direction);
}
