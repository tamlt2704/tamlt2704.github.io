var assert = require('assert')
var {db, Row} = require('../jsqlite')


var r = new Row(1, 'foo', 'foobar@gmail.com')
assert(r.userId === 1)
assert(r.userName === 'foo')
assert(r.userEmail === 'foobar@gmail.com')

db.insert(r)
r.userId = 2
db.insert(r)
r.userId = 3
db.insert(r)

db.select()
console.log( 'all test passed!')


