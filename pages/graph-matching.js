const graph = [
    [0, 16, 13, 0,  0,  0],
    [0, 0,  10, 12, 0,  0],
    [0, 4,  0,  0,  14, 0],
    [0, 0,  9,  0,  0,  20],
    [0, 0,  0,  7,  0,  4],
    [0, 0,  0,  0,  0,  0]
]

const n = 6

/*
 * return true if there is a path from source to target
*/
const BFS = (s, t, parent) => {
    let visited = Array(n).fill(false)
    var queue = []

    queue.push(s)
    visited[s] = true
    while (queue.length) {
        let u = queue.shift()
        graph[u].forEach((v, i) => {
            if (!visited[i] && (v > 0)) {
                queue.push(i)
                visited[i] = true
                parent[i] = u
            }
        })
    }

    return visited[t]
}

const ForkFulkerson = (source, sink) => {
    let parent = Array(n).fill(-1)

    let max_flow = 0

    while(BFS(source, sink, parent)) {
        let path_flow = Number.MAX_SAFE_INTEGER
        let s = sink
        while (s != source) {
            path_flow = Math.min(path_flow, graph[parent[s]][s])
            s = parent[s]
        }

        max_flow += path_flow

        let v = sink
        while (v != source) {
            let u = parent[v]
            graph[u][v] -= path_flow
            graph[v][u] += path_flow
            v = parent[v]
        }
    }

    return max_flow
}

let source = 0, sink = 5;
console.log( ForkFulkerson(source, sink) )
