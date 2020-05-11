class Sodoku {
    cross(A, B) {
        A = (typeof A == 'string') ? A.split('') : A;
        B = (typeof B == 'string') ? B.split('') : B;
        var crossed = [];
        A.forEach(a => {
            B.forEach(b => {
                crossed.push(a+b);
            });
        });
        return crossed;
    }

    constructor() {
        this.digits = '123456789'.split(''); // ['1', '2', ... , '8', '9']
        this.rows = 'ABCDEFGHI'.split('')
    }
}
