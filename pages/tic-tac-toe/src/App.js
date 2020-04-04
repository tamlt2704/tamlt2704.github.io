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
                {squares: Array(9).fill(null)}
            ],
            stepNumber: 0,
            xIsNext: true
        }
    }
   
    computerThinkAndPlay() {
        console.log('computer think and play');
        const history = this.state.history.slice(0, this.state.stepNumber + 1);
        const current = history[history.length - 1];
        const squares = current.squares.slice();

        // get first empty square 
        for (let i = 0; i < squares.length; i++) {
            if (!squares[i]) {
                var nextPosition = i;
                console.log(nextPosition);
                squares[nextPosition] = this.state.xIsNext ? "X" : "O";


                this.setState({
                    history: history.concat([
                        {
                            squares: squares
                        }
                    ]),
                    stepNumber: history.length,
                    xIsNext: !this.state.xIsNext
                }, () => { 
                    console.log(this.state);
                }
                );
                break;
            }
        }
    }

    handleClick(i) {
        const history = this.state.history.slice(0, this.state.stepNumber + 1);
        const current = history[history.length - 1];
        const squares = current.squares.slice();
        
        if (calculateWinner(squares) || squares[i]) {
            return;
        }


        const isComputerTurn = this.state.xIsNext ? false : true;
        
        if (!isComputerTurn) {
            console.log(`game click event ${i}`);
            squares[i] = this.state.xIsNext ? "X" : "O";
            console.log(squares);
            console.log(history.concat([{squares: squares}]));
            this.setState({
                history: history.concat([
                    {
                        squares: squares
                    }
                ]),
                stepNumber: history.length,
                xIsNext: !this.state.xIsNext
            }, () => {
                console.log('call back');
                console.log(this.state);
                this.computerThinkAndPlay()
            });
        } 

    }

    render() {
        const history = this.state.history;
        const current = history[this.state.stepNumber];
        let status;
        let winner = calculateWinner(current.squares);
        if (winner) {
            status = "Winner: " + winner;
        } else {
            status = "Next player: " + (this.state.xIsNext ? "X" : "O");
            console.log(status);
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
