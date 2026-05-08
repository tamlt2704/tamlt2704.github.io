# Chapter 9: Undo Everything — Command

[← Chapter 8: Strategy](chapter-08-strategy.md) | [Chapter 10: Observer →](chapter-10-observer.md)

---

## The Pain

Mira's top feature request: undo. Dev's first attempt:

```java
public class DocumentEditor {
    private Document document;

    public void addBlock(Block block) {
        document.getBlocks().add(block);
        // How do we undo this? We'd need to remember what was added...
    }

    public void deleteBlock(int index) {
        document.getBlocks().remove(index);
        // Undo means we need the deleted block back... where did it go?
    }

    public void moveBlock(int from, int to) {
        Block block = document.getBlocks().remove(from);
        document.getBlocks().add(to, block);
        // Undo means... move it back? What were from and to again?
    }

    public void replaceText(int blockIndex, String oldText, String newText) {
        // Undo means... we need to store oldText somewhere
    }

    // No undo. No redo. No macro recording. Users lose work.
}
```

Every operation directly mutates state. There's no record of what happened, no way to reverse it, and no way to replay actions.

## The Pattern: Command

Encapsulate each action as an object with `execute()` and `undo()`:

```java
public interface Command {
    void execute();
    void undo();
    String description();  // For undo history UI
}

public class AddBlockCommand implements Command {
    private final Document document;
    private final Block block;
    private final int position;

    public AddBlockCommand(Document document, Block block, int position) {
        this.document = document;
        this.block = block;
        this.position = position;
    }

    @Override
    public void execute() {
        document.getBlocks().add(position, block);
    }

    @Override
    public void undo() {
        document.getBlocks().remove(position);
    }

    @Override
    public String description() {
        return "Add " + block.getType() + " block";
    }
}

public class DeleteBlockCommand implements Command {
    private final Document document;
    private final int position;
    private Block deletedBlock;  // Stored for undo

    public DeleteBlockCommand(Document document, int position) {
        this.document = document;
        this.position = position;
    }

    @Override
    public void execute() {
        deletedBlock = document.getBlocks().remove(position);
    }

    @Override
    public void undo() {
        document.getBlocks().add(position, deletedBlock);
    }

    @Override
    public String description() {
        return "Delete " + deletedBlock.getType() + " block";
    }
}
```

## The Command History

```java
public class CommandHistory {
    private final Deque<Command> undoStack = new ArrayDeque<>();
    private final Deque<Command> redoStack = new ArrayDeque<>();

    public void execute(Command command) {
        command.execute();
        undoStack.push(command);
        redoStack.clear();  // New action invalidates redo history
    }

    public void undo() {
        if (undoStack.isEmpty()) return;
        Command command = undoStack.pop();
        command.undo();
        redoStack.push(command);
    }

    public void redo() {
        if (redoStack.isEmpty()) return;
        Command command = redoStack.pop();
        command.execute();
        undoStack.push(command);
    }

    public List<String> undoHistory() {
        return undoStack.stream().map(Command::description).toList();
    }
}
```

## Macro Recording: Composite Commands

Users record macros — sequences of commands replayed as one:

```java
public class MacroCommand implements Command {
    private final String name;
    private final List<Command> commands;

    public MacroCommand(String name, List<Command> commands) {
        this.name = name;
        this.commands = List.copyOf(commands);
    }

    @Override
    public void execute() {
        commands.forEach(Command::execute);
    }

    @Override
    public void undo() {
        // Undo in reverse order
        var reversed = new ArrayList<>(commands);
        Collections.reverse(reversed);
        reversed.forEach(Command::undo);
    }

    @Override
    public String description() { return "Macro: " + name; }
}

// Recording a macro
public class MacroRecorder {
    private List<Command> recording;
    private boolean isRecording;

    public void startRecording() {
        recording = new ArrayList<>();
        isRecording = true;
    }

    public MacroCommand stopRecording(String name) {
        isRecording = false;
        return new MacroCommand(name, recording);
    }

    public void record(Command command) {
        if (isRecording) recording.add(command);
    }
}
```

## The Editor with Commands

```java
public class DocumentEditor {
    private final Document document;
    private final CommandHistory history;
    private final MacroRecorder macroRecorder;

    public DocumentEditor(Document document) {
        this.document = document;
        this.history = new CommandHistory();
        this.macroRecorder = new MacroRecorder();
    }

    public void addBlock(Block block, int position) {
        var cmd = new AddBlockCommand(document, block, position);
        history.execute(cmd);
        macroRecorder.record(cmd);
    }

    public void deleteBlock(int position) {
        var cmd = new DeleteBlockCommand(document, position);
        history.execute(cmd);
        macroRecorder.record(cmd);
    }

    public void undo() { history.undo(); }
    public void redo() { history.redo(); }
}
```

## PlugBoard After Command

Before: No undo, no redo, no macros. Users lose work. Operations directly mutate state with no record.

After: Every action is an object. Full undo/redo. Macro recording. History visible in the UI.

```java
editor.addBlock(new ParagraphBlock("Hello"), 0);
editor.addBlock(new CodeBlock("x = 1", "python"), 1);
editor.undo();  // Removes the code block
editor.undo();  // Removes the paragraph
editor.redo();  // Paragraph is back
```

## When NOT to Use Command

| Situation | Why Not | Alternative |
|---|---|---|
| Actions aren't undoable (send email) | Can't reverse side effects | Event log without undo |
| Simple CRUD with no history | Command objects add overhead | Direct method calls |
| Undo state is too large (video editing) | Memory explosion | Checkpoint/snapshot |
| Single non-repeatable action | No benefit from encapsulation | Direct call |

## What You Learned

- **Command** — encapsulate a request as an object with execute/undo
- **Command History** — stack-based undo/redo with clear-on-new-action semantics
- **Macro Command** — composite of commands, undo in reverse order
- **Separation** — the invoker (editor) doesn't know what the command does internally
- **Extensibility** — new commands don't change the history or editor code

Next: when a block changes, the sidebar, toolbar, and preview panel all need to update. But they don't know about each other. That's Observer.

---

[← Chapter 8: Strategy](chapter-08-strategy.md) | [Chapter 10: Observer →](chapter-10-observer.md)
