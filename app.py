import numpy as np
import matplotlib.pyplot as plt
import svgwrite
import cairosvg
import cv2
import csv
import io

def image_to_csv(png_path, csv_path):
    """Convert PNG image to CSV file."""
    # Load and preprocess image
    image = cv2.imread(png_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
    
    # Detect contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        for i, contour in enumerate(contours):
            for point in contour:
                writer.writerow([i, point[0][0], point[0][1]])

def read_csv(csv_path):
    """Read CSV file and convert to path_XYs."""
    np_path_XYs = np.genfromtxt(csv_path, delimiter=',')
    path_XYs = []
    for i in np.unique(np_path_XYs[:, 0]):
        npXYs = np_path_XYs[np_path_XYs[:, 0] == i][:, 1:]
        XYs = []
        for j in np.unique(npXYs[:, 0]):
            XY = npXYs[npXYs[:, 0] == j][:, 1:]
            XYs.append(XY)
        path_XYs.append(XYs)
    return path_XYs

def plot(paths_XYs):
    """Plot paths from path_XYs."""
    fig, ax = plt.subplots(tight_layout=True, figsize=(8, 8))
    for XYs in paths_XYs:
        for XY in XYs:
            ax.plot(XY[:, 0], XY[:, 1], linewidth=2)
    ax.set_aspect('equal')
    plt.show()

def polylines2svg(paths_XYs, svg_path):
    """Convert polylines to SVG and save it."""
    W, H = 0, 0

    for path_XYs in paths_XYs:
        for XY in path_XYs:
            W, H = max(W, np.max(XY[:, 0])), max(H, np.max(XY[:, 1]))

    padding = 0.1
    W, H = int(W + padding * W), int(H + padding * H)
    dwg = svgwrite.Drawing(svg_path, profile='tiny', shape_rendering='crispEdges')
    group = dwg.g()
    
    for path in paths_XYs:
        for XY in path:
            path_data = []
            path_data.append(("M", (XY[0, 0], XY[0, 1])))
            for j in range(1, len(XY)):
                path_data.append(("L", (XY[j, 0], XY[j, 1])))
            group.add(dwg.path(d=' '.join([f"{cmd} {x},{y}" for cmd, (x, y) in path_data]), fill='none', stroke='black', stroke_width=2))
    
    dwg.add(group)
    dwg.save()
    png_path = svg_path.replace('.svg', '.png')
    cairosvg.svg2png(url=svg_path, write_to=png_path, parent_width=W, parent_height=H, output_width=W, output_height=H, background_color='white')

def main():
    image_path = 'upload.png'
    csv_path = 'frag0.csv'
    svg_path = 'output.svg'
    
    # Convert PNG image to CSV
    image_to_csv(image_path, csv_path)
    
    # Read CSV, plot, and save to SVG
    path_XYs = read_csv(csv_path)
    plot(path_XYs)
    polylines2svg(path_XYs, svg_path)

if __name__ == '__main__':
    main()
