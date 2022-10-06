# James Carey Necron_Life_Counter
# https://github.com/carey-james/Necron_Life_Counter

import board
from time import sleep
from adafruit_ht16k33.ht16k33 import HT16K33
from busio import I2C
from adafruit_seesaw import seesaw, rotaryio

NUMBERS = (
    0x3F,  # 0
    0x06,  # 1
    0x5B,  # 2
    0x4F,  # 3
    0x66,  # 4
    0x6D,  # 5
    0x7D,  # 6
    0x07,  # 7
    0x7F,  # 8
    0x6F,  # 9
)

STARTLIFE = 40
BRIGHTNESS = 0.5

class Seg7x4(HT16K33):

    POSITIONS = (0, 2, 6, 8)  #  The positions of characters.

    def __init__(
        self,
        i2c: I2C,
        address: Union[int, List[int], Tuple[int, ...]] = 0x70,
        auto_write: bool = True
    ) -> None:
        super().__init__(i2c, address, auto_write)
        self._chars = 4
        self._bytes_per_buffer = 4

    def _adjusted_index(self, index: int) -> int:
        offset = (index // self._bytes_per_buffer) * self._buffer_size
        return offset + self.POSITIONS[index % self._bytes_per_buffer]

    def set_digit_raw(self, index: int, bitmask: int) -> None:
        """Set digit at position to raw bitmask value. Position should be a value
        of 0 to 3 with 0 being the left most digit on the display.

        :param int index: The index of the display to set
        :param int bitmask: A single byte number corresponding to the segments to set
        """
        if not isinstance(index, int) or not 0 <= index < self._chars:
            raise ValueError(
                f"Index value must be an integer in the range: 0-{self._chars - 1}"
            )

        # Set the digit bitmask value at the appropriate position.
        self._set_buffer(self._adjusted_index(index), bitmask & 0xFF)

        if self._auto_write:
            self.show()

# Set up the led display
i2c = board.I2C()
display = Seg7x4(i2c)
display.brightness = BRIGHTNESS
display.set_digit_raw(0,NUMBERS[4])
display.set_digit_raw(1,NUMBERS[0])

seesaw = seesaw.Seesaw(board.I2C(), 0x36)

encoder = rotaryio.IncrementalEncoder(seesaw)
seesaw.pin_mode(24, seesaw.INPUT_PULLUP)

last_position = 0
life = STARTLIFE

# Run Loop
while True:

    # negate the position to make clockwise rotation positive
    # position = -encoder.position
    position = encoder.position

    if position != last_position:

        if (position > last_position) & (life < 99):
            life += 1
        elif (life > 0):
            life -= 1 
        else:
            pass

        print(life)

        display.set_digit_raw(0,NUMBERS[life//10])
        display.set_digit_raw(1,NUMBERS[life%10])


    last_position = position
