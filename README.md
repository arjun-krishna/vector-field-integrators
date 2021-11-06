# Interactive Vector Field integrators

![Application Layout](demo/ivecintegrator.png?raw=true "Application Layout")

Built using PyGame

To launch the application run:
```bash
pip install -r requirements.txt
python app.py
```

The UI provides the following interactions:
- insert (points can be inserted)
- delete (click near point to delete)
- clear (delete all points)
- multi-select (select multiple points to configure a common integrator config)
- right click on point to configure a particular points integrator config
- points can be grabbed and dragged across the grid

Integrator config:
- Three options to click on euler/midpoint/rk4
- All three options can be selected a comparitive animation of all the trajectories is displayed via colored trails
- Color code
  - RED: Explicit Euler
  - GREEN: Midpoint
  - BLUE: RK4

NOTE: 
- There are kinks in the system! The major vulnerability is that there is no
validation being performed on the text input. I plan to change these to sliders element 
in the future.
- The vector field text input (considers x, y variables and uses python eval) - using eval
is dangerous as this is not properly validated. If there are any evaluation errors the vector
field component is treated as 0
- No validation on integrator configs as well, so the system can break on wrong options.
