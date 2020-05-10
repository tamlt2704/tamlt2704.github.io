var counter= 0;
class Sodoku {
    constructor() {
        const digits = '123456789'.split('');
        const rows = 'ABCDEFGHI'.split('');
        const cols = digits;
        const rss = ['ABC', 'DEF', 'GHI'].map(x => x.split(''));
        const css = ['123', '456', '789'].map(x => x.split(''));
        this.parsingDone = false;
        this.squares = this.cross(rows, cols)
        this.unitlist = [
            ...cols.map(c => this.cross(rows, [c])),
            ...rows.map(r => this.cross([r], cols)),
            ...rss.map(rs => css.map(cs => this.cross(rs, cs))).flat(),
        ];
        this.units = this.squares.reduce((hash, s) => {
            hash[s] = this.unitlist.filter(u => u.indexOf(s) >= 0);
            return hash;
        }, {});
        this.peers = this.squares.reduce((hash, s) => {
            hash[s] = [...new Set(this.units[s].flat())].filter(x => x != s);
            return hash;
        }, {});
    }

    cross(A, B) {
        return A.map(a => B.map(b => a + b)).flat();
    }

    test() {
        console.assert(1===1);
        console.assert(this.squares.length == 81);
        console.assert(this.unitlist.length == 27);
        console.assert(this.squares.every(s => this.units[s].length == 3));
        console.assert(this.squares.every(s => this.peers[s].length == 20));
        // TODO
        // units[C2]
        // peers[C2]
        //
        var grid = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......";
        var gridParsedResult = this.grid_values(grid.split(''));
        console.assert(gridParsedResult['A1'] == '4');
        console.log('all test pass.');
    }

    /* 
     * Convert grid to a dict of possible values, {square: digits} or
     * return False if a contradiction is detected
    */
    parse_grid(grid) {
        const digits = '123456789';
        var values = this.squares.reduce((hash, s) => {
            hash[s] = '123456789';
            return hash;
        }, {});
    
        for (let [s, d] of Object.entries(this.grid_values(grid))) {
            if (digits.includes(d) && !this.assign(values, s, d)) {
                return false;
            }
        }
        this.parsingDone = true;
        return values;
    }
    
    /* eliminate all the other values (except d) from values[s] and propagate
     * Return values, except return False if a contradiction is detected
     */
    assign(values, s, d) {
        var other_values = values[s].replace(d, '').split('');
        other_values.forEach(d2 => {
            if (!this.eliminate(values, s, d2)) {
                return false;
            }
        });
        return values;
    }
    
    /*
     * eliminate d from values[s]; propagate when values or places <= 2
     * return values, except return false if a contradiction is detected
     */
    eliminate(values, s, d) {
        if (!values[s].includes(d)) {
            return values;            // already eliminated
        }
        values[s] = values[s].replace(d, '');
        // (1) if squares s is reduced to one value d2, then eliminate d2 from
        // the peers
        if (values[s].length == 0) {
            return false;   // contradiction: removed last value
        } else if (values[s].length == 1) {
            var d2 = values[s];
            this.peers[s].forEach(s2 => {
                if (!this.eliminate(values, s2, d2)) {
                    return false;
                }
            });
        }

        // (2) if a unit u is reduced to only one place for a value d, then put
        // it there
        this.units[s].forEach(u => {
            var dplaces = u.filter(s => values[s].includes(d));
            if (dplaces.length == 0) {
                return false;               // contradiction no place for this value
            } else if (dplaces.length == 1) {
                // d can be only in one place in unit; assign it there
                if (!this.assign(values, dplaces[0], d)) {
                    return false;
                }
            }
        });
    }
    
    solve(grid) {
        return this.search(this.parse_grid(grid));
    }
    
    search(values) {
        console.log(`search function ${counter}`);
        this.display_grid(values);

        if (!values) {
            return false; // failed earlier
        } 
        if (this.squares.every(s => values[s].length == 1)) {
            return values; // solved
        }

        // choose the unfilled square s with the fewest possibilities
        var [s, n] = this.squares
                            .filter(s => values[s].length > 1)
                            .map(s => [s, values[s].length])
                            .sort((x, y) => x[1] - y[1])[0];

        values[s].split('').forEach(d => {
            //var solution = this.search(this.assign(Object.assign({}, values), s, d));
            var solution = this.search(this.assign({...values}, s, d));
            if (solution) {
                return solution;
            }
        })
        counter++;
        return false;
    }
    /*
     * Convert grid to a dict of {square: char} with '0' or '.' for empties
     * ex: grid:
     * 4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......
     * """
     * 4 . . |. . . |8 . 5 
     * . 3 . |. . . |. . . 
     * . . . |7 . . |. . . 
     * ------+------+------
     * . 2 . |. . . |. 6 . 
     * . . . |. 8 . |4 . . 
     * . . . |. 1 . |. . . 
     * ------+------+------
     * . . . |6 . 3 |. 7 . 
     * 5 . . |2 . . |. . . 
     * 1 . 4 |. . . |. . . 
     * """
     */
    grid_values(grid) {
        const digits = '123456789';
        var chars = grid.filter(c => (digits.indexOf(c) > -1) || ('0.'.indexOf(c) > -1))
        console.assert(chars.length == 81);
        return Object.fromEntries(this.squares.map((s, i) =>  [s, chars[i]]));
    }
    
    alignCenter(x, width) {
        var startPadding = ' '.repeat((width - x.length)/2);
        return startPadding + x + ' '.repeat(width - startPadding.length - x.length);

    }
    display_grid(values) {
        var width = 1 + Math.max(...this.squares.map(s => values[s].length));
        var line = Array(3).fill('-'.repeat(width*3)).join('+');
        const rows = 'ABCDEFGHI'.split('');
        const cols = '123456789'.split('');
        for(let r of rows) {
            console.log(cols.map(c => (this.alignCenter(values[r+c], width) + ('36'.includes(c)?'|':''))).join(''));
            if ('CF'.includes(r)) {
                console.log(line);
            }

        }
    }
}


var s = new Sodoku();
s.test();
var grid = "400000805030000000000700000020000060000080400000010000000603070500200000104000000";
var grid1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
var grid2 = '400000805030000000000700000020000060000080400000010000000603070500200000104000000'
var grid3 = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
var grid4 = '48.3............71.2.......7.5....6....2..8.............1.76...3.....4......5....';
s.solve(grid4.split(''));
//s.display_grid(s.solve(grid2.split('')));
//s.display_grid(s.parse_grid(grid1.split('')));

module.exports = {
    s: new Sodoku(),
};
