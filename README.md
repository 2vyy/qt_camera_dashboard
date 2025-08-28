# Security Camera Dashboard
A desktop-based security monitoring application built with Python, PyQt, and OpenCV. Designed for real-time surveillance across multiple camera feeds, with motion detection, automated recording, and a customizable user interface.

## Features
 - **Multi-Camera Support**: Dynamically display multiple live video feeds in a grid layout  
- **Motion Detection**: Background subtraction and contour analysis for detecting movement  
- **Auto Recording**: Automatically records motion events with timestamped video output  
- **Customizable UI**: Live-adjustable detection sensitivity, light/dark theme toggle  
- **Persistent Settings**: Saves user preferences using `QSettings`  
- **Multi-Threading**: Uses `QThread` to handle concurrent camera streams efficiently
- 
## Future Improvements
- Logging system
- Notification alerts on motion detection  
- Support for wireless video streams over a network
