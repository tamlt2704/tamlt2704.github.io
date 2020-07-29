import React from 'react';
import logo from './logo.svg';
import './App.css';

function Square(props) {
    return (
        <button className="square" onClick={props.onClick}>
            {props.value}
        </button>
    )
}
class Board extends React.Component {
    
    renderSquare(i) {
        return (
            <Square 
                value={this.props.squares[i]}
                onClick={() => this.props.onClick(i)}
            />
        );
    }

    render() {
        return (
            <div> 
                <div className="board-row">
                    {this.renderSquare(0)}
                    {this.renderSquare(1)}
                    {this.renderSquare(2)}
                </div>
                <div className="board-row">
                    {this.renderSquare(3)}
                    {this.renderSquare(4)}
                    {this.renderSquare(5)}
                </div>
                <div className="board-row">
                    {this.renderSquare(6)}
                    {this.renderSquare(7)}
                    {this.renderSquare(8)}
                </div>
            </div>
        )
    }
}

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            history: [
                //{squares: Array(9).fill(null)}
                {squares: [null, null, null, null, null, null, null, null, null]}
            ],
            stepNumber: 0,
            xIsNext: true 
        }
    }
   
    // X: Max
    // O: Min (computer)
    /*
    alphaBetaMinimax(squares, alpha, beta, maximizingPlayer) {
        var player = maximizingPlayer ? 'X' : 'O';
        var winner = calculateWinner(squares);
        var bestPosition = null;
        console.log(squares
            .map(x => x!=null? x : '*')
            .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
            .replace(/,/g, '')
        );
        console.log(`current player ${player}`);
        //if (winner === player) {
        if (winner === player) {
            console.log(`(${alpha}: ${beta}) ${maximizingPlayer ? "max" : "min"} return 1`);
            return [-1, bestPosition];
        } else if (winner != null ) {
            console.log(`(${alpha}: ${beta}) ${maximizingPlayer ? "max" : "min"} return -1`);
            return [1, bestPosition];
        } else {
            // board is full
            if (squares.every(x => x)) {
                console.log('tie');
                return [0, bestPosition];
            } 
        }
        console.log('continue');

        if (maximizingPlayer) {
            var value = -2;
            for (let i = 0; i < 9; i++) {
                if (!squares[i]) {
                    squares[i] = player; //X
                    var [a, pos] = this.alphaBetaMinimax(
                        squares.slice(), alpha, beta, false);
                    if (a > value) {
                        value = a;
                        bestPosition = i;
                    }
                    squares[i] = null;

                    if (value >= beta) { 
                        i = 10; 
                    } //break for loop

                    if (value > alpha) {
                        alpha = value
                    }
                }
            }
            return [value, bestPosition];
        } else {
            var value = 2;
            for (let i = 0; i < 9; i++) {
                if (!squares[i]) {
                    squares[i] = player; // O
                    console.log('min set value for: ' + i + ':' + player); 
                    var [b, pos] = this.alphaBetaMinimax(
                        squares.slice(), alpha, beta, true);
                    if (b < value) {
                        value = b;
                        bestPosition = i;
                    }
                    squares[i] = null;
                    if (alpha >= value) { 
                        i = 10; 
                    } //break for loop

                    if (value < beta) {
                        beta = value;
                    }
                }
            }
            return [value, bestPosition];
        }
    }
    */
    minF(squares, depth, trace) {
        var minv = 2
        var bestPosition = null;
        var winner = calculateWinner(squares);

        console.log('minF'+ depth);
        if (winner === 'X') {
            console.log(squares
                .map(x => x!=null? x : '*')
                .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
                .replace(/,/g, '')
            );
            console.log('return ' + [-1, bestPosition]);
            return [-1, bestPosition];
        } else if (winner === 'O') {
            console.log(squares
                .map(x => x!=null? x : '*')
                .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
                .replace(/,/g, '')
            );
            console.log('return ' + [1, bestPosition]);
            return [1, bestPosition];
        } else if (squares.every(x => x)) {
            console.log('tie')
            console.log(squares
                .map(x => x!=null? x : '*')
                .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
                .replace(/,/g, '')
            );
            console.log('return ' + [0, bestPosition]);
            return [0, bestPosition];
        }

        for (let i = 0; i < 9; i++) {
            if (!squares[i]) {
                squares[i] = 'X';
                var [m, p] = this.maxF(squares.slice(), depth+1);
                if (m < minv) {
                    minv = m;
                    bestPosition = i;
                }
                squares[i] = null;
            }
        }
        console.log('return' + [minv, bestPosition]);
        return [minv, bestPosition];
    }

    maxF(squares, depth) {
        var maxv = -2;
        var bestPosition = null;
        var winner = calculateWinner(squares);

        console.log('maxF'+ depth);
        if (winner === 'X') {
            console.log(squares
                .map(x => x!=null? x : '*')
                .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
                .replace(/,/g, '')
            );
            console.log('return ' + [-1, bestPosition]);
            return [-1, bestPosition];
        } else if (winner === 'O') {
            console.log(squares
                .map(x => x!=null? x : '*')
                .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
                .replace(/,/g, '')
            );
            console.log('return ' + [1, bestPosition]);
            return [1, bestPosition];
        } else if (squares.every(x => x)) {
            console.log('tie')
            console.log(squares
                .map(x => x!=null? x : '*')
                .map((x, i) => (i+1) % 3 ? x : x + '\n').join()
                .replace(/,/g, '')
            );
            console.log('return ' + [0, bestPosition]);
            return [0, bestPosition];
        }

        for (let i = 0; i < 9; i++) {
            if (!squares[i]) {
                squares[i] = 'O';
                var [m, p] = this.minF(squares.slice(), depth+1);
                if (m > maxv) {
                    maxv = m;
                    bestPosition = i;
                }
                squares[i] = null;
            }
        }
        console.log('return' + [maxv, bestPosition]);
        return [maxv, bestPosition];
    }

    findNextPosition(squares) {
        /*var [value, nextPosition] = this.alphaBetaMinimax(
            squares.slice(), -2, 2, false);
            */
        var trace = {};
        var [value, nextPosition] = this.maxF(squares.slice(), 0, trace);
        console.log(value, nextPosition);
        return nextPosition;
    }

    computerThinkAndPlay() {
        const history = this.state.history.slice(0, this.state.stepNumber + 1);
        const current = history[history.length - 1];
        const squares = current.squares.slice();

        var foundId = this.findNextPosition(squares);
        if (foundId) {
            squares[foundId] = this.state.xIsNext ? 'X' : 'O';
        }

        this.setState({
            history: history.concat([{squares: squares}]),
            stepNumber: history.length,
            xIsNext: !this.state.xIsNext
        });
    }
    
    componentDidUpdate(prevProps, prevState) {
        console.log('componentDidUpdate');
        const isComputerTurn = this.state.xIsNext ? false : true;
        if (isComputerTurn) {
            this.computerThinkAndPlay();
        }
    }

    handleClick(i) {
        const history = this.state.history.slice(0, this.state.stepNumber + 1);
        const current = history[history.length - 1];
        const squares = current.squares.slice();
        
        const isComputerTurn = this.state.xIsNext ? false : true;
        
        let winner = calculateWinner(squares);
        if (!winner) {
            if (!isComputerTurn) {
                if (!squares[i]) {
                    squares[i] = this.state.xIsNext ? "X" : "O";
                    this.setState({
                        history: history.concat([
                            {
                                squares: squares
                            }
                        ]),
                        stepNumber: history.length,
                        xIsNext: !this.state.xIsNext
                    });
                }
            } 
        }
    }

    render() {
        const history = this.state.history;
        const current = history[history.length - 1];
        let status;
        let winner = calculateWinner(current.squares);

        if (winner) {
            status = "Winner: " + winner;
        } else {
            status = "Next player: " + (this.state.xIsNext ? "X" : "O");
        }

        return (
            <div className="game">
                <div className="game-board">
                    <Board
                        squares={current.squares}
                        onClick={i => this.handleClick(i)}
                    />
                </div>

                <div className="gameInfo">
                    <div> {status} </div> 
                </div>
            </div>
        )
    }

}

function calculateWinner(squares) {
        const lines = [
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8],
                [0, 3, 6],
                [1, 4, 7],
                [2, 5, 8],
                [0, 4, 8],
                [2, 4, 6]
            ];
        for (let i = 0; i < lines.length; i++) {
                const [a, b, c] = lines[i];
                if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
                        return squares[a];
                        }
            }
        return null;
}
export default App;
