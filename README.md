# Forbidden
![python 3.8](https://img.shields.io/badge/python-3.8-blue) ![pygame-ce 2.5.2](https://img.shields.io/badge/pygamece-2.5.2-green) ![moderngl 5.7.4](https://img.shields.io/badge/moderngl-5.7.4-purple)

Forbidden is a small interactive ocean scene rendered in pixel art style. It isn’t quite a game (at least not yet) its more of a visual demo, quiet, and atmospheric. A lone boat drifts in dark waters, surrounded by rocky spires, veiled in fog. Under the surface, schools of fish weave through tall kelp forests.

![alt text](https://github.com/LuckeyDuckey/Forbidden/blob/main/Data/Images/Banner.png)

## Usage

To run Forbidden simply follow these steps (you’ll need Python 3.8 or newer):

1. Clone or download this repository:
   ```bash
   git clone https://github.com/LuckeyDuckey/Forbidden.git
   ```

2. Install dependencies using pip:
   ```bash
   pip install moderngl pygame-ce numpy
   ```

5. Run the program:
   ```bash
   cd Forbidden
   python Main.py
   ```

Once running, you can move the camera around using WASD, and interact with the world using the mouse. Your cursor appears as a white circle rendered inside the scene, clicking fills it in, which then allows you to move the kelp and cause the fish the scatter. You can also resize the circle using the scroll wheel.

The project also includes a configuration file `Data/Settings.json` you can use it to adjust resolution, toggle fullscreen, set the maximum FPS, or change sound levels. Here’s the what it looks like with the default configuration:

```json
{
    "SceneResolution": [640, 360],
    "ScreenResolution": [1280, 720],
    "FullScreen": false,

    "SoundsVolume": 1.0,
    "MusicVolume": 1.0,

    "ShowDebug": true,
    "FpsCap": 144
}
```

For example, if you want to run the project in fullscreen mode at 60 FPS, simply set `"FullScreen": true` and `"FpsCap": 60`. The settings are loaded automatically when the program starts.

## Technical Details

### 🌊 Ocean Waves

The surface of the ocean is generated using a sum of sine waves technique, a classic approach for simulating water motion without calculating fluid dynamics. Each wave is defined by amplitude, frequency, direction, and speed, and when many are combined, the interference between them creates natural looking wave patterns. This method is efficient, as it can be GPU accelerated via ModernGL shaders, and offers good control over the ocean conditions.

Learn more: [Effective Water Simulation from Physical Models (GPU Gems, NVIDIA)](https://developer.nvidia.com/gpugems/gpugems/part-i-natural-effects/chapter-1-effective-water-simulation-physical-models)

### 🐟 Fish Behavior

The fish in Forbidden use the Boids algorithm, originally developed by Craig Reynolds in 1986. Each fish follows three simple rules (separation, alignment, and cohesion) which together produce complex, organic flocking behavior. The algorithm is written in C++ and connected to python using pybind11, for efficiency.

Learn more: [Craig Reynolds’ original Boids paper](https://www.red3d.com/cwr/boids)

### 🌿 Kelp Simulation

Each kelp strand is simulated as a Verlet chain. A sequence of connected points constrained by fixed distances. Verlet integration is simple while being stable, making it ideal for soft, flexible bodies like plants or ropes. Like the fish simulation, the Verlet solver is implemented in C++ to minimize CPU overhead.

Learn more: [Verlet Integration based ropes Explained](https://toqoz.fyi/game-rope.html)

### ⚙️ WindowHandler

One of the small but practical tools in this project is `Scripts/WindowHandler.py` its a script that improves how Pygame handles window resizing and moving. By default, Pygame windows freeze while being resized or moved, and there’s no built in way to lock aspect ratio. WindowHandler solves both problems. To use it, simply import and instantiate it (both parameters are optional):

```python
from WindowHandler import WindowHandler

Window = WindowHandler(AspectRatio = 16 / 9, MinWindowSize = 150)
```

That’s all you need, no extra setup required. Internally, the script hooks into the Windows API, intercepting and replacing windows default event handling. It prevents freezing when the windows is moving or being resized, and enforces a consistent aspect ratio. The optional MinWindowSize parameter prevents the windows from becoming too small.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
