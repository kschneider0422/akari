
from copy import deepcopy
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import matplotlib.patches as patches



class Board:
    
    vectors = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    serial_number = 0
    
    def __init__(self, dims=(6, 6), givens=None):
        self.dims = dims
        rows, cols = dims
        self.pool = {(i, j) for i in range(rows) for j in range(cols)}
        self.locked = set()
        if givens is None:
            givens = {}
        self.givens = deepcopy(givens)
        for cell, val in givens.items():
            self.pool.discard(cell)
            if val < 0:
                self.locked.add(cell)
        
        self.empty = set()
        self.illuminated = set()
        self.lights = set()
        self.serial_number = Board.serial_number
        Board.serial_number += 1
        
        self.border = set([(-1, _) for _ in range(cols)]
                          + [(rows, _) for _ in range(cols)]
                          + [(_, -1) for _ in range(rows)]
                          + [(_, cols) for _ in range(rows)])
        
    def copy(self):
        new = Board(self.dims, self.givens)
        new.pool = deepcopy(self.pool)
        new.locked = deepcopy(self.locked)
        new.empty = deepcopy(self.empty)
        new.illuminated = deepcopy(self.illuminated)
        new.lights = deepcopy(self.lights)
        new.border = deepcopy(self.border)


        return new
    
    def check_given(self, cell, val):

        
        r, c = cell
        nbrs = set([(r + dr, c + dc) for dr, dc in Board.vectors])
        
        lts = nbrs & self.lights
        mts = nbrs & self.pool
        
        if len(lts) > val:
            return [False, False]
        
        if len(lts) == val:
            for mt in mts:
                self.empty.add(mt)
                self.pool.discard(mt)
            self.locked.add(cell)
            return [True, True]

        if len(lts) + len(mts) == val:
            for mt in mts:
                self.add_light(mt)
            self.locked.add(cell)
            return [True, True]
        
        if len(lts) + len(mts) < val:
            return [False, False]
            
        
        return [True, False]
    
    def check_givens(self):
        restart = True
        while restart is True:
            restart = False
            for cell, val in self.givens.items():
                if cell in self.locked:
                    continue
                test, restart = self.check_given(cell, val)
                if test is False:

                    return False
                if restart is True:
                    break
        return True
    
    
    def check_empty(self, cell):
        
        blockers =  set(self.givens) | self.border
        row, col = cell
        for dr, dc in Board.vectors:
            current = (row + dr, col + dc)
            while current not in blockers:
                if current in self.pool:
                    return True
                r, c = current
                current = (r + dr, c + dc)
                
        return False
    
    def check_empties(self):

        for cell in self.empty:
            test =  self.check_empty(cell)
            if test is False:
                return False
        return True
            
    def add_light(self, cell):
        
        illuminable = self.pool | self.empty | self.illuminated
        row, col = cell
        for dr, dc in Board.vectors:
            current = (row + dr, col + dc)
            while current in illuminable:
                self.illuminated.add(current)
                self.empty.discard(current)
                self.pool.discard(current)
                r, c = current
                current = (r + dr, c + dc)
                
        self.lights.add(cell)
        self.pool.discard(cell)
            


    def children(self):

        light_child = self.copy()
        dark_child = self.copy()
        cell = min(self.pool)
        light_child.add_light(cell)
        dark_child.empty.add(cell)
        dark_child.pool.discard(cell)
  
        return [light_child, dark_child]
    

    def __str__(self):

        rows, cols = self.dims
        out = []
        for row in range(rows):
            row_out = ""
            for col in range(cols):
                tup = (row, col)
                if tup in self.givens:
                    val = self.givens[tup]
                    if val >= 0:
                        row_out += f"[{val}]"
                    else:
                        row_out += "[ ]"

                elif tup in self.lights:
                    row_out += " O "
                elif tup in self.pool:
                    row_out += " . "
                elif tup in self.illuminated:
                    row_out += "   "
                else:
                    row_out += " x "
            out.append(row_out)
        return "\n".join(out)

    __repr__ = __str__
    
    
    def plot(self):
        rows, cols = self.dims
        fig, ax = plt.subplots()
        fig.set_size_inches(rows, cols)
        ax.set_aspect(1)
        ax.axis('off')
        ax.set_xlim([0, 100 * cols])
        ax.set_ylim([0, 100 * rows])
    
        # draw background grid
        for row in range(rows + 1):
            if row == 0 or row == rows:
                c = '#000000' # black
                z = 5
            else:
                c = '#cccccc' # light gray
                z = 0
            xs = [0, cols * 100]
            ys = [row * 100, row * 100]
            line = mlines.Line2D(xs, ys, color = c, zorder = z)
            ax.add_line(line)     
        for col in range(cols + 1):
            if col == 0 or col == cols:
                c = '#000000' # black
                z = 5
            else:
                c = '#cccccc' # light gray
                z = 0
            xs = [col * 100, col * 100]
            ys = [0, rows * 100]
            line = mlines.Line2D(xs, ys, color = c, zorder = z)
            ax.add_line(line)
    

        # Shaded cells
        for cell in set(self.givens):
            row, col = cell
            rect = patches.Rectangle((100 * col, 100 * rows - 100 * (row + 1)), 
                                     100, 100, 
                                     facecolor='#000000', 
                                     edgecolor='#000000',
                                     zorder = -5)
            ax.add_patch(rect)
            
        # Put numbers in cells
        for cell, val in self.givens.items():
            if val < 0:
                continue
            row, col = cell
            ax.text(100 * (col + 1) - 50, 100 * rows - 100 * (row + 1) + 50, 
                    val, size = 18, color='#ffffff',
                    horizontalalignment = 'center',
                    verticalalignment = 'center',
                    zorder = 10)

            
        # Add lights
        for cell in self.lights:
            row, col = cell
            
            
            circ = patches.Circle((100 * (col + 1) - 50, 
                                   100 * rows - 100 * (row + 1) + 50),
                                  35, edgecolor='#000000', fill=False,
                                  zorder=5)
            ax.add_patch(circ)
            
            
        # Illuminate cells

        for cell in set(self.lights | self.illuminated):
            row, col = cell
            rect = patches.Rectangle((100 * col, 100 * rows - 100 * (row + 1)), 
                                     100, 100, 
                                     facecolor='#ffffe0', 
                                     edgecolor='#cccccc',
                                     zorder = -5)
            ax.add_patch(rect)
            
        
        # Empty cells

        for cell in self.empty:
            row, col = cell
            rect = patches.Rectangle((100 * col, 100 * rows - 100 * (row + 1)), 
                                     100, 100, 
                                     facecolor='#dddddd', 
                                     edgecolor='#cccccc',
                                     zorder = -5)
            ax.add_patch(rect)
            
        
        return fig


class Akari:
    def __init__(self, dims=(6, 6), givens=None):
        self.dims = dims
        if givens is None:
            givens = {}
        self.givens = deepcopy(givens)
        self.board = Board(dims, givens)
        self.solutions = []

    def solve(self, max_sols=2):

        C = self.board.copy()
        if C.check_givens() is False:
            return
        if C.check_empties() is False:
            return

        stack = [C]
        
        count = 0
        while len(stack) > 0:
            
            
            current = stack.pop()
            # indices = [_.serial_number for _ in stack]
            # print(indices, current.serial_number)
            left, right = current.children()
            if left.check_givens() is True and left.check_empties() is True:
                if len(left.lights) + len(left.givens) + len(left.illuminated) == self.dims[0] * self.dims[1]:
                    self.solutions.append(left)
                else:
                    
                    if len(left.pool) > 0:
                        stack.append(left)

            if right.check_givens() is True and right.check_empties() is True:
                if len(right.lights) + len(right.givens) + len(right.illuminated) == self.dims[0] * self.dims[1]:
                    self.solutions.append(right)
                else:
                    if len(right.pool) > 0:
                        stack.append(right)



            if max_sols > 0 and len(self.solutions) >= max_sols:
                break
            
            count += 1
            if count % 100000 == 0:
                print(count, 
                      len(stack), 
                      len(self.solutions), 
                      stack[0].serial_number,
                      stack[0:10][-1].serial_number,
                      stack[0:20][-1].serial_number,
                      stack[0:30][-1].serial_number,
                      current.serial_number)
                print([_.serial_number for _ in stack[0:10]])
                print([_.serial_number for _ in stack[10:20]])
                print([_.serial_number for _ in stack[20:30]])
                print([_.serial_number for _ in stack[30:40]])
                print()
            
            if count % 1000000 == 0:
                current.plot()

