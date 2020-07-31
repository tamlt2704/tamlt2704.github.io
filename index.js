var readline = require('readline')
const CMD_PROMPT = 'db >'
const DB_CONST = {
    'META_COMMAND_SUCCESS': 1,
    'META_COMMAND_UNRECOGNIZED': -1,
    'PREPARE_SUCCESS': 2,
    'PREPARE_STATEMENT_UNRECOGNIZED': -2,
    'STATEMENT_INSERT': 3,
    'STATEMENT_SELECT': 4,
    'PAGE_SIZE': 4096,
    'TABLE_MAX_PAGES': 100,
    'ID_SIZE': 4,
    'USERNAME_SIZE': 32,
    'EMAIL_SIZE': 255,
    'EXECUTE_SUCCESS': 'EXECUTE_SUCCESS',
    'PREPARE_STATEMENT_ERROR': 'PREPARE_STATEMENT_ERROR',
    'EXECUTE_TABLE_FULL': 'EXECUTE_TABLE_FULL'
}

Object.assign(
    DB_CONST, {
        'ROW_SIZE': DB_CONST.ID_SIZE + DB_CONST.USERNAME_SIZE + DB_CONST.EMAIL_SIZE,
        'ROWS_PER_PAGES': DB_CONST.PAGE_SIZE / DB_CONST.ROW_SIZE,
        'TABLE_MAX_ROWS': DB_CONST.ROWS_PER_PAGES * DB_CONST.TABLE_MAX_PAGES,
    }
)

var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

function exit_db() {
    console.log( 'Have a great day!' )
    process.exit(0)
}

class Row {
    constructor(id, username, email) {
        this.id = id
        this.username = username 
        this.email = email 
    }
}

// return a buffer
function serialize_row(row) {
    var buffer = Buffer.alloc(256)
    var id = buffer.slice(0, 4)
    var username = buffer.slice(4, 32)
    var email = buffer.slice(32, 255)

    id.write(row.id)
    username.write(row.username)
    email.write(row.email)
    return buffer
}

// return a row
function deserialize_row(buff) {
    var id = buff.slice(0, buff.indexOf(0x00, 0)).toString('utf-8').trim()
    var username = buff.slice(4, buff.indexOf(0x00, 4)).toString('utf-8').trim()
    var email = buff.slice(32, buff.indexOf(0x00, 32)).toString('utf-8').trim()
    return new Row(id, username, email)
}

class Statement {
    constructor() {
        this.statementType = null;
        this.row = null
    }
}

class Table {
    constructor() {
        this.num_rows = 0
        this.pages = Array(DB_CONST.TABLE_MAX_PAGES).fill(null)
    }
}

function do_meta_command(command) {
    if (command === '.exit') {
        exit_db()
    } else {
        return DB_CONST.META_COMMAND_UNRECOGNIZED
    }
}

function prepare_statement(command, statement) {
    if (command.startsWith('insert')) {
        statement.statementType = DB_CONST.STATEMENT_INSERT
        let insert_pattern = /insert ([\d]+) ([\w]+) ([\w@.-]+)/
        let match = command.match(insert_pattern)
        if (!match || (match.length !== 4)) {
            return DB_CONST.PREPARE_STATEMENT_ERROR
        }
        
        return DB_CONST.PREPARE_SUCCESS
    } else if (command.startsWith('select')) {
        statement.statementType = DB_CONST.STATEMENT_SELECT
        return DB_CONST.PREPARE_SUCCESS
    }
    return DB_CONST.PREPARE_STATEMENT_UNRECOGNIZED
}

function execute_insert(statement, table) {
    if (table.num_rows >= DB_CONST.TABLE_MAX_ROWS) {
        return DB_CONST.EXECUTE_TABLE_FULL
    }
    
    return DB_CONST.EXECUTE_SUCCESS;
}

function execute_select(statement, table) {
    return DB_CONST.EXECUTE_SUCCESS;
}

function execute_statement(statement, table) {
    switch (statement.statementType) {
        case DB_CONST.STATEMENT_INSERT:
            return execute_insert(statement, table)
        case DB_CONST.STATEMENT_SELECT:
            return execute_select(statement, table)
    }
}

table = new Table()

rl.on('line', command => {
    command = command.trim().toLowerCase()

    if (command.startsWith('.')) {
        switch (do_meta_command(command)) {
            case DB_CONST.META_COMMAND_UNRECOGNIZED:
                console.log( 'unrecognized command' )
                break;
        }
    } else {
        let statement = new Statement();
        switch(prepare_statement(command, statement)) {
            case DB_CONST.PREPARE_SUCCESS:
                switch(execute_statement(statement, table)) {
                    case DB_CONST.EXECUTE_SUCCESS:
                        console.log( 'Executed!' )
                        break
                    case DB_CONST.EXECUTE_TABLE_FULL:
                        console.log( 'Error: Table Full!' )
                        break
                }
                break
            case DB_CONST.PREPARE_STATEMENT_ERROR:
                console.log( 'syntax error' )
                break
            case DB_CONST.PREPARE_STATEMENT_UNRECOGNIZED:
                console.log( 'unrecognized statement' )
                break
        }
    }

    rl.setPrompt(CMD_PROMPT, CMD_PROMPT.length)
    rl.prompt()
}).on('close', () => {
    exit_db()
})

// rl.setPrompt(CMD_PROMPT, CMD_PROMPT.length)
// rl.prompt()
