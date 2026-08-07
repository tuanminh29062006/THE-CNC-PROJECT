import re
import tkinter as tk

def parse(self):
    if not self.gcode_text.get("1.0", tk.END).strip(): return
    self.run_button.config(state = tk.NORMAL)
    self.motions = []
    current_g = -1
    row_lines = self.gcode_text.get(1.0, tk.END).split('\n')
    line_order = 0
    
    for line in row_lines:
        # Remove notes within (...)
        # Shorten Form
        line = re.sub(r'\(.*?\)', '', line).split(';')[0].strip()
        # Instead of: print(line[0].strip())
        # To deal with empty line[0]
        if not line: continue
        matches = self.parse_pattern.findall(line)
        for index, (key, value) in enumerate(matches):
            if value in ('90', '91'): # Kết quả của findall lu
                matches[index] = ('C', value)

        if matches:
            cmd = {key: float(value) for (key, value) in matches}
            #print(cmd)
            if line_order == 0 and 'C' not in cmd:
                cmd['C'] = int(90.0)

            if 'C' in cmd:
                cmd['C'] = int(cmd['C'])
                current_c = cmd['C']
            else:
                cmd['C'] = current_c

            """
            if line_order == 1 and 'G' not in cmd:
                self.log(f"The loaded G-Code file is not valid, missing G- at line {line_order}\n")
                return
            """
            if 'P' in cmd:
                cmd['P'] = int(cmd['P'])

            if 'G' in cmd:
                # Fix the G0.0 -> G0
                cmd['G'] = int(cmd['G'])
                current_g = cmd['G']
            # Fix lines that don't have G
            elif any(axis in cmd for axis in ['X', 'Y', 'Z', 'I', 'J', 'F', 'R']) and line_order != 0:
                cmd['G'] = current_g

            if cmd.get('G') in [0, 1, 2, 3, 21] or cmd.get('C') in [90, 91]:
                self.motions.append(cmd)
                #print(self.motions)
            else:
                self.log(f"The command G{cmd.get('G')} is not available within the \nprogram ability\n")
                return
            line_order += 1
    #print(self.motions)
        # Normal Form
        #line = re.sub(r'\(.*?\)', '', line).split(';')
        #for segment in line:
        #    if(line.index(segment) == 0):
        #        segment.strip()
    