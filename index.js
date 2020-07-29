var readline = require('readline')
const CMD_PROMPT = 'db >'
const STATUS = {
    'META_COMMAND_SUCCESS': 1,
    'META_COMMAND_UNRECOGNIZED_COMMAND': -1
}

var rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
})

function exit_db() {
    console.log( 'Have a great day!' )
    process.exit(0)
}

function do_meta_command(command) {
    if (command === '.exit') {
        exit_db()
    } else {
        return STATUS.META_COMMAND_UNRECOGNIZED_COMMAND
    }
}

rl.on('line', command => {
    command = command.trim()

    if (command.startsWith('.')) {
        switch (do_meta_command(command)) {
            case STATUS.META_COMMAND_UNRECOGNIZED_COMMAND:
                console.log( 'unrecognized command' )
                break;
        }
    }

    rl.setPrompt(CMD_PROMPT, CMD_PROMPT.length)
    rl.prompt()
}).on('close', () => {
    exit_db()
})

rl.setPrompt(CMD_PROMPT, CMD_PROMPT.length)
rl.prompt()
