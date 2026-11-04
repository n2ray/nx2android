using System;
using System.Collections.Generic;

// Match updates to the selected program ID, not to another program in a multi-program package.
static class ProgramChoice {
    internal static T Pick<T>(IEnumerable<T> values, Func<T, ulong> title, Func<T, bool> patch, ulong? id, bool wantPatch) where T : class {
        T result = null; ulong chosen = 0; bool ambiguous = false;
        foreach (T value in values) {
            if (patch(value) != wantPatch) continue;
            ulong next = title(value);
            if (id.HasValue && id.Value != next) continue;
            if (result == null || (!id.HasValue && next < chosen)) { result = value; chosen = next; ambiguous = false; }
            else if (next == chosen) ambiguous = true;
        }
        if (ambiguous) throw new InvalidOperationException("multiple matching program NCAs; cannot choose a version safely");
        return result;
    }
}
