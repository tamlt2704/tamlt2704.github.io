def cross(A: String, B:String): Array[String] = {
  (for (a <- A; b <- B) yield s"$a$b").toArray
}

val digits = "123456789"
val rows = "ABCDEFGHI"
val cols = digits
val squares = cross(rows, cols)
val unitlist = (rows.toArray.map(r => cross(r.toString, cols)) ++
               cols.toArray.map(c => cross(rows, c.toString)) ++
               (for (rs <- Array("ABC", "DEF", "GHI");
                     cs <- Array("123", "456", "789")
                    ) yield cross(rs, cs))
               )
val units = squares.map(s => s -> unitlist.filter(_ contains s)).toMap
val peers = squares.map(s => s -> units(s).flatten.filter(_ != s).toSet).toMap


def test() = {
  assert(squares.size == 81)
  assert(unitlist.size == 27)
  assert(squares.map(s => units(s).size).forall(_ == 3))
  assert(squares.map(s => peers(s).size).forall(_ == 20))
  val unit_C2 = (Array(
    Array("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"),
    Array("A2", "B2", "C2", "D2", "E2", "F2", "G2", "H2", "I2"),
    Array("A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3")))
  assert(units("C2").deep == unit_C2.deep)
  val peers_C2 = Set("A2", "B2", "D2", "E2", "F2", "G2", "H2", "I2",
                       "C1", "C3", "C4", "C5", "C6", "C7", "C8", "C9",
                       "A1", "A3", "B1", "B3")
  assert(peers("C2") == peers_C2)
}

val grid1  = "003020600900305001001806400008102900700000008006708200002609500800203009005010300"
val grid2  = "4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......"
val hard1  = ".....6....59.....82....8....45........3........6..3.54...325..6.................."

def parse_grid(grid: String): collection.mutable.Map[String, String] = {
  val values = collection.mutable.Map(squares.map(s => s -> digits): _*)
  for ((s, d) <- grid_values(grid)) {
    if ((digits contains d) && (assign(values, s, d) != null)) {
      return null
    }
  }
  return values
}

def grid_values(grid: String): collection.mutable.Map[String, String] = {
  val chars = grid.filter(c => (digits contains c) || ("0." contains c))
  assert(chars.length == 81)
  return collection.mutable.Map(
    (for ((s, c) <- squares.zip(chars)) yield (s -> c.toString)): _*
  )
}

def assign(values: collection.mutable.Map[String, String], s: String, d: String): collection.mutable.Map[String, String] = {
  val other_values = values(s).replaceAll(d, "")
  if (other_values.map(d2 => eliminate(values, s, d2.toString)).forall(_ != null)) {
    return values
  } else {
    return null
  }
}

def eliminate(values: collection.mutable.Map[String, String], s: String, d: String): collection.mutable.Map[String, String] = {
  if (!values(s).contains(d)) {
    return values
  }
  values(s) = values(s).replaceAll(d, "")

  if (values(s).length == 0) {
    return null
  } else if (values(s).length == 1) {
    val d2 = values(s)
    if (!peers(s).map(s2 => eliminate(values, s2, d2)).forall(_ != null)) {
      return null
    }
  }

  for (u <- units(s)) {
    val dplaces = u.filter(s => values(s).contains(d))
    println(dplaces)
    if (dplaces.length == 0) {
      return null
    } else if (dplaces.length == 1) {
      if (assign(values, dplaces(0), d) == null) {
        return null
      }
    }
  }
  return values
}

def display(values: collection.mutable.Map[String, String]):Unit = {
  val width = 1 + squares.map(s => values(s).length).max
  val line = "\n" + Range(0, 3).map(_ => ("-" * (width * 3))).mkString("+")
  for (r <- rows) {
    for (c <- cols) {
      print(values(r.toString + c) + " " + (if ("36" contains c) "|" else ""))
    }
    if ("CF" contains r) println(line) else println("")
  }
  println("")
}
//grid_values(grid2)
println(grid1)
display(parse_grid(grid1))
//test()
