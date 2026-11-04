using System;
using System.Collections.Generic;

sealed class Entry { public ulong Id; public bool Patch; public Entry(ulong id, bool patch) { Id = id; Patch = patch; } }
static class Test {
    static void Main() {
        var entries = new List<Entry> { new Entry(2, true), new Entry(2, false), new Entry(2, false), new Entry(1, true), new Entry(1, false) };
        Entry Pick(ulong? id, bool patch) => ProgramChoice.Pick(entries, e => e.Id, e => e.Patch, id, patch);
        if (Pick(null, false).Id != 1 || !Pick(1, true).Patch || Pick(3, true) != null) throw new Exception("incorrect program selection");
        entries.Add(new Entry(1, true));
        try { Pick(1, true); throw new Exception("ambiguous update accepted"); }
        catch (InvalidOperationException) { }
        Console.WriteLine("program selection passed");
    }
}
