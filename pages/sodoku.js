class Sodoku {
    constructor() {
        const digits = '123456789'.split('');
        const rows = 'ABCDEFGHI'.split('');
        const cols = digits;
        const rss = ['ABC', 'DEF', 'GHI'].map(x => x.split(''));
        const css = ['123', '456', '789'].map(x => x.split(''));
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
            return false;            // already eliminated
        }
        values[s] = values[s].replace(d, '');

        // (1) if squares s is reduced to one value d2, then eliminate d2 from
        // the peers
        if (values[s].length == 0) {
            return false;
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

    display_grid(values) {
        console.log(values);
    }
}


var s = new Sodoku();
s.test();
var grid = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......";
var grid1 = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
var grid2 = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

s.display_grid(s.parse_grid(grid2.split('')));

module.exports = {
    s: new Sodoku(),
};
