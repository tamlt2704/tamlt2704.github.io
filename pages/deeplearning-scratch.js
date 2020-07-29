// forward propagation

var math = require('./math.min.js')
var asciichart = require('./asciichart.js')

function demo_forwardProgpagation() {
    // 1 input, 1 weights, 1 output
    let numberOfToes = [8.5, 9.5, 10, 9];
    let input = numberOfToes[0];
    let weight = 0.1;

    let pred = input * weight;
    console.log(pred) //0.85

    // 1 input, multiple weights, 1 output
    let toes = [8.5, 9.5, 9.9, 9.0];
    let wlrec = [0.65, 0.8, 0.8, 0.9];
    let nfans = [1.2, 1.3, 0.5, 1.0];
    let weights = [0.1, 0.2, 0];
    input = [toes[0], wlrec[0], nfans[0]];

    pred = math.multiply(input, weights)
    console.log(pred) // 0.98

    // multiple input, multiple weights, multiple output
    input = [toes[0], wlrec[0], nfans[0]];
    weights = [
        [0.1, 0.1, -0.3], // hurt
        [0.1, 0.2, 0.0],  // win
        [0.0, 1.3, 0.1]   // sad
    ];

    pred = math.multiply(input, math.transpose(weights))
    console.log(pred);

    // neural networks can be stacked
    console.log('hidden layer')
    let ih_wgt = [
        [0.1, 0.2, -0.1], // hidden layer
        [-0.1, 0.1, 0.9],
        [0.1, 0.4, 0.1]
    ];
    let hp_wgt = [
        [0.3, 1.1, -0.3],
        [0.1, 0.2, 0.0],
        [0.0, 1.3, 0.1]
    ];
    weights = [ih_wgt, hp_wgt]
    input = [toes[0], wlrec[0], nfans[0]];
    hid = math.multiply(input,  math.transpose(weights[0])); // layer 1
    pred = math.multiply(hid, math.transpose(weights[1]));
    console.log(pred)
}

function demo_gradientDescent() {
    let input = 0.5;
    let goal_pred = 0.8;
    let weight = 0.5;
    let pred = input * weight;
    let error = Math.pow(pred - goal_pred, 2)
    console.log(error) //0.3

    // calculating direction and amount from error
    weight = 0.5
    goal_pred = 0.8
    input = 0.5
    for (let i = 0; i < 20; i++) {
        pred = input * weight;
        error = Math.pow(pred - goal_pred, 2)
        let direction_and_ammount = (pred - goal_pred) * input
        weight = weight - direction_and_ammount 
        console.log(error, pred)
    }

    // prediction exploded example, and how to use alpha to reduce
    weight = 0.5
    goal_pred = 0.8
    input = 2
    const alpha = 0.1

    for (let i = 0; i < 20; i++) {
        pred = input * weight;
        error = Math.pow(pred - goal_pred, 2)
        let direction_and_ammount = (pred - goal_pred) * input
        weight = weight - direction_and_ammount * alpha
        console.log(error, pred)
    }
}

//demo_forwardProgpagation()
demo_gradientDescent()


