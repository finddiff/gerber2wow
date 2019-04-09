from PIL import Image


_IgnoreMovementLargerThan = 15 # in mm

class Layer:
    """Implement one layer of SLA with all linked parameters"""
    def __init__(self, number):
        self.thickness = 0.1
        self.exposition_time = 15
        self.move_time = 0
        self.number = number
        self.speed_up = 10
        self.speed_down = 10
        self.up_distance = 10
        self.down_distance = 10
        self.exposition = 255
        self.data = b""
        self.width = 0
        self.height = 0
        # self.image = None
        # self.illuminated_pixel = 0

    def set_image(self, pngImg):
        # self.width = size[0]
        # self.height = size[1]
        # self.image = Image.frombytes("1", size, data, "raw", "1;R")
        self.image = pngImg
        self.width = self.image.size[0]
        self.height = self.image.size[1]
        self.image = self.image.rotate(-90, expand=True)
        self.data = self.image.tobytes("raw", "1;R")
        # TODO: Run that in the background
        # self.illuminated_pixel = sum(_b2ba[int(b)] for b in data)

    # def update_movetime(self):
    #     if self.speed_up > 0 or self.speed_down > 0:
    #         self.move_time = abs(self.up_distance) / (self.speed_up / 60)
    #         self.move_time += abs(self.up_distance - self.thickness) / (self.speed_down / 60)
    #     else:
            # Absurdely huge number to show that there is a problem
            # (movement set to 0 is not a wanted value)
            # self.move_time = 9999999

    def get_packed_image(self):
        return self.data

    # def set_exposition(self, value):
    #     self.exposition = value


def _nothing(code, cur_layer):
    """Stub for unused gcode command"""
    pass


def _g1(code, cur_layer):
    """Decode gcode G1 command"""
    distance = 0
    speed = 0

    for param in code:
        if param[0] == "Z" or param[0] == "z":
            distance = float(param[1:])
            if abs(distance) <= _IgnoreMovementLargerThan:

                if distance > 0:
                    cur_layer.up_distance = distance
                else:
                    cur_layer.down_distance = distance

                cur_layer.thickness += distance
                cur_layer.thickness = round(cur_layer.thickness, 5)
                if speed is not 0:
                    cur_layer.move_time += abs(distance) / (speed / 60)
                    if distance > 0:
                        cur_layer.speed_up = speed
                    else:
                        cur_layer.speed_down = speed

        elif param[0] == "F" or param[0] == "f":
            speed = float(param[1:])
            if distance is not 0:
                cur_layer.move_time += abs(distance) / (speed / 60)
                if distance > 0:
                    cur_layer.speed_up = speed
                else:
                    cur_layer.speed_down = speed


def _g4(code, cur_layer):
    """Decode gcode G4 command"""
    for param in code:
        if param[0] == "S" or param[0] == "s":
            value = float(param[1:])
            # Ending have a really long pause, don't change layer exposition if it is longer than 120 seconds
            if value <= 120:
                cur_layer.exposition_time += value


def _m106(code, cur_layer):
    """Decode gcode M106 command"""
    if cur_layer is not None:
        for param in code:
            if param[0] == "S" or param[0] == "s":
                value = float(param[1:])
                if value > 0:
                    cur_layer.set_exposition(value)

class WowFile:
    _GCodes = {
        "G21": _nothing,  # Set unit to millimetre
        "G91": _nothing,  # Set positioning to relative
        "M17": _nothing,  # Set On/Off all steppers
        "M106": _m106,  # UV Backlight power
        "G28": _nothing,  # Move to origin (Homing)
        "M18": _nothing,  # Move to origin (Homing)
        "G1": _g1,  # Move
        "G4": _g4,  # Sleep
    }

    _Preamble = "G21;\n" \
                "G91;\n" \
                "M17;\n" \
                "M106 S0;\n" \
                "G28 Z0;\n" \
                ";W:{W};\n" \
                ";H:{H};\n"

    _Ending = "M106 S0;\n" \
              "G1 Z20.0;\n" \
              "G4 S300;\n" \
              "M18;"

    _LayerStart = ";L:{layer:d};\n" \
                  "M106 S0;\n" \
                  "G1 Z{up:,g} F{spdu:g};\n" \
                  "G1 Z{down:,g} F{spdd:g};\n" \
                  "{{{{\n"

    _LayerEnd = "\n" \
                "}}}}\n" \
                "M106 S{exp:g};\n" \
                "G4 S{wait:g};\n"

    def __init__(self):
        self.layers = []
        self.Height = 0
        self.Width = 0

    def write_wow(self, filename):
        with open(filename, "wb") as f:
            # First write file preamble
            f.write(self._Preamble.format(H=self.Height, W=self.Width).encode("ascii"))

            for l in self.layers:
                # Write layer preamble
                f.write(self._LayerStart.format(layer=l.number,
                                                up=l.up_distance,
                                                down=round(l.thickness - l.up_distance, 5),
                                                spdu=l.speed_up,
                                                spdd=l.speed_down).encode("ascii"))
                # Write layer image
                f.write(l.get_packed_image())
                # Write layer ending
                f.write(self._LayerEnd.format(exp=l.exposition,
                                              wait=l.exposition_time).encode("ascii"))

            # Write ending
            f.write(self._Ending.encode("ascii"))