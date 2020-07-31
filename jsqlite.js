const COLUMN_ID_SIZE = 4
const COLUMN_USERNAME_SIZE = 32
const COLUMN_EMAIL_SIZE = 255
const ROW_SIZE = COLUMN_ID_SIZE + COLUMN_USERNAME_SIZE + COLUMN_EMAIL_SIZE

const ID_OFFSET = 0
const USERNAME_OFFSET = ID_OFFSET + COLUMN_ID_SIZE
const EMAIL_OFFSET = USERNAME_OFFSET + COLUMN_USERNAME_SIZE

const TABLE_MAX_PAGES = 100
const PAGE_SIZE = 4096
const ROW_PER_PAGE = PAGE_SIZE / ROW_SIZE
const TABLE_MAX_ROWS = ROW_PER_PAGE * TABLE_MAX_PAGES



const EXECUTE_TABLE_FULL = 'EXECUTE_TABLE_FULL'
const INSERT_ERROR_EXCEPTION = 'INSERT_ERROR_EXCEPTION'
const INSERT_SUCCESS = 'INSERT_SUCCESS'

const DB_CONST = {
    EXECUTE_TABLE_FULL,
}

class Logger {
    info(msg) {
        console.log(msg)
    }
    error(msg) {
        console.error(msg)
    }
}

let logger = new Logger()

class Table {
    constructor() {
        this.num_rows = 0
        this.pages = Array(TABLE_MAX_PAGES).fill(null)
    }
}

class Row {
    constructor(id = null, name = null, email = null) {
        this.buff = Buffer.alloc(ROW_SIZE)
        this.id = this.buff.slice(ID_OFFSET, COLUMN_ID_SIZE)
        this.username = this.buff.slice(USERNAME_OFFSET, COLUMN_USERNAME_SIZE)
        this.useremail = this.buff.slice(EMAIL_OFFSET, COLUMN_EMAIL_SIZE)
        if (id && name && email) {
            this.id.writeInt8(id)
            this.username.write(name)
            this.useremail.write(email)
        }
    }

    static deserialize(buff) {
        let r = new Row()
        buff.copy(r.buff)
        return r
    }

    get userId() {
        return this.id.readInt8()
    }

    get userEmail() {
        let buff = this.useremail
        return buff.slice(0, buff.indexOf(0x00)).toString('utf-8').trim()
    }

    get userName() {
        let buff = this.username
        return buff.slice(0, buff.indexOf(0x00)).toString('utf-8').trim()
    }

    set userId(id) {
        this.setUserId(id)
    }
    set userEmail(email) {
        this.setUserEmail(email)
    }
    set userName(name) {
        this.setUserName(name)
    }

    setUserId(id) {
        this.id.writeInt8(id)
    }
    setUserName(name) {
        this.username.write(name)
    }
    setUserEmail(email) {
        this.useremail.write(email)
    }

    toString() {
        return `${this.userId} : ${this.userName} : ${this.userEmail}`
    }
}

class Statement {
    constructor() {
        this.statementType = null
        this.row_to_insert = null
    }
}

class Jsqlite {
    constructor() {
        this.table = new Table()
    }

    get_row_slot(row_number) {
        let page_num = row_number / ROW_PER_PAGE | 0 // get integer
        let pages = this.table.pages
        if (!pages[page_num]) {
            pages[page_num] = Buffer.alloc(PAGE_SIZE)
        }
        let page = pages[page_num]
        let row_offset = row_number % ROW_PER_PAGE
        let byte_offset = row_offset * ROW_SIZE
        return page.slice(byte_offset, byte_offset + ROW_SIZE)
    }

    insert(row) {
        if (this.table.num_rows >= TABLE_MAX_ROWS) {
            return EXECUTE_TABLE_FULL
        }
        try {
            let bytesCopied = row.buff.copy(this.get_row_slot(this.table.num_rows))
            if (bytesCopied !== ROW_SIZE) {
                return INSERT_ERROR_EXCEPTION
            }
        } catch (err) {
            logger.error(err)
            return INSERT_ERROR_EXCEPTION
        }
        this.table.num_rows += 1
        return INSERT_SUCCESS
    }

    select() {
        for(let i = 0; i < this.table.num_rows; i++) {
            var buff = this.get_row_slot(i)
            logger.info( Row.deserialize(buff).toString())
        }
    }
}

exports.db = new Jsqlite()
exports.Row = Row
