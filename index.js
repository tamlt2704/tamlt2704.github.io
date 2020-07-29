var readline = require('readline')
const CMD_PROMPT = 'db >'
const STATUS = {
    'META_COMMAND_SUCCESS': 1,
    'META_COMMAND_UNRECOGNIZED': -1,
    'PREPARE_SUCCESS': 2,
    'PREPARE_STATEMENT_UNRECOGNIZED': -2,
    'STATEMENT_INSERT': 3,
    'STATEMENT_SELECT': 4
}

var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

function exit_db() {
    console.log( 'Have a great day!' )
    process.exit(0)
}

class Statement {
    constructor() {
        this.statementType = null;
    }
}

function do_meta_command(command) {
    if (command === '.exit') {
        exit_db()
    } else {
        return STATUS.META_COMMAND_UNRECOGNIZED
    }
}

function prepare_statement(command, statement) {
    if (command.startsWith('insert')) {
        statement.statementType = STATUS.STATEMENT_INSERT
        return STATUS.PREPARE_SUCCESS
    } else if (command.startsWith('select')) {
        statement.statementType = STATUS.STATEMENT_SELECT
        return STATUS.PREPARE_SUCCESS
    }
    return STATUS.PREPARE_STATEMENT_UNRECOGNIZED
}

function execute_statement(statement) {
    switch (statement.statementType) {
        case STATUS.STATEMENT_INSERT:
            console.log( 'this is where we would do an insert' )
            break
        case STATUS.STATEMENT_SELECT:
            console.log( 'this is where we would do an select' )
            break
    }
}

rl.on('line', command => {
    command = command.trim().toLowerCase()

    if (command.startsWith('.')) {
        switch (do_meta_command(command)) {
            case STATUS.META_COMMAND_UNRECOGNIZED:
                console.log( 'unrecognized command' )
                break;
        }
    } else {
        let statement = new Statement();
        switch(prepare_statement(command, statement)) {
            case STATUS.PREPARE_SUCCESS:
                execute_statement(statement)
                console.log( 'Executed!' )
                break
            case STATUS.PREPARE_STATEMENT_UNRECOGNIZED:
                console.log( 'unrecognized statement' )
                break
        }
    }

    rl.setPrompt(CMD_PROMPT, CMD_PROMPT.length)
    rl.prompt()
}).on('close', () => {
    exit_db()
})

rl.setPrompt(CMD_PROMPT, CMD_PROMPT.length)
rl.prompt()
