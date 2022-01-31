from math import sqrt
import tkinter as tk

def readFile():
    data = []
    maxi = 0
    mini = 0
    with open("QTable.txt", "r") as f:
        f.readline() # useless top lines
        f.readline()
        inLine = f.readline()
        while inLine != "":
            line = [float(x) for x in inLine[5:].split("  ")]
            if max(line) > maxi:
                maxi = max(line)
            if min(line) < mini:
                mini = min(line)
            data.append(line)
            inLine = f.readline()
    return data, maxi, mini
                
        
def getColourFromValue(value, maxi, mini):
    if value == 0:
        return "#FFFFFF"
    if value < 0:
        # value = -(sqrt(abs(value)))
        # mini = -(sqrt(abs(mini)))
        h = "{:02x}".format(255 - int((value/mini) * 255))
        b = "{:02x}".format(int((1-(value/mini)) * 255))
        return f"#FF{h}{b}"
    # value = sqrt(value)
    # maxi = sqrt(maxi)
    h = "{:02x}".format(255- int((value/maxi) * 255))
    b = "{:02x}".format(int((1-(value/maxi)) * 255))
    return f"#{h}FF{b}"
    

def renderData(data, maxi, mini):
    width = len(data[0])*10
    height = len(data)*10
    root = tk.Tk()
    root.minsize(width, height)
    frame = tk.Frame(root, width=width, height=height)
    canvas = tk.Canvas(frame, width=width, height=height)
    frame.pack()
    canvas.pack()

    for y, line in enumerate(data):
        for x, value in enumerate(line):
            colour = getColourFromValue(value, maxi, mini)
            canvas.create_rectangle(x*10, y*10, (x*10)+10, (y*10)+10, fill=colour, outline="" )


    root.mainloop()

def main():
    data, maxi, mini = readFile()
    renderData(data, maxi, mini)


if __name__ == "__main__":
    main()
    