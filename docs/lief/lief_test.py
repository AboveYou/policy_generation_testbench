# testing the lief implementation
# (does not work properly in Chestnut)
import lief
import sys
import os

filename = sys.argv[1]

# parse the binary
binary = lief.ELF.parse(filename)

# create and add note
note = lief.ELF.Note("UNKNOWN", lief.ELF.NOTE_TYPES.UNKNOWN, [21, 187])
# in newer versions a constructor need to be used
# note = lief.ELF.Note.create(name="IAIK", type=lief.ELF.Note.TYPE.UNKNOWN, decription=syscalls)
if note is None:
    print("Error! Note is None")
    exit(1)
note = binary.add(note)

new_binary = os.path.join(filename + "_modified")
# inject sandboxing library
binary.add_library("libsandboxing.so")
binary.write(new_binary)
