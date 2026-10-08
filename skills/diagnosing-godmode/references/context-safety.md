# Context safety for session transcripts

One transcript record can be larger than a megabyte or contain a full
history. If you print one full record, it can overflow the context of the
session that does the diagnosis. Each reader of a session file, controller
or subagent, follows these rules for each file, each time.

1. **Measure before reading.**

   ```bash
   wc -lc "$F"
   awk '{ if (length($0) > 100000) print NR, length($0) }' "$F"   # long lines
   ```

2. **Never `cat` or `grep` for content.** First get line numbers and counts
   (`grep -n … | cut -d: -f1`, `jq -r '.type' | sort | uniq -c`). Then get
   small fields from specific lines (`sed -n Np | jq -c '{…}'` or
   `| cut -c1-500`). Use the field-extraction commands that discovery
   established for the source in front of you.
3. **Narrow anything over 500 characters.** If a command returns more than
   500 characters for one record, make the field or the slice smaller.
4. **Read-only.** Never change, move, or remove a session file.
