# Fowler Code Smell Baseline

Source: _Refactoring_ by Martin Fowler, ch. 3.

These 12 smells apply to each Standards review in godmode, in addition to the documented standards of the repository. Two rules control them:

- **The repo overrides.** A documented standard of the repository always wins. If it endorses something that the baseline would flag, do not report the smell.
- **Always a judgement call.** Each smell is a labeled heuristic ("possible Feature Envy"), never a hard violation. Skip each item that tooling already enforces.

---

- **Mysterious Name**: A function, variable or type whose name does not show what it does or holds. Rename it. If no honest name comes, the design is not clear.
- **Duplicated Code**: The same logic shape occurs in more than one hunk or file. Extract the shared shape, and call it from both.
- **Feature Envy**: A method that uses the data of a different object more than its own data. Move the method to the data that it envies.
- **Data Clumps**: The same few fields or parameters go together again and again (a type that wants to exist). Put them into one type.
- **Primitive Obsession**: A primitive or string that stands in for a domain concept that should have its own type. Give the concept its own small type.
- **Repeated Switches**: The same switch/if-cascade on the same type occurs again in the change. Replace it with polymorphism, or with one map that both sites share.
- **Shotgun Surgery**: One logical change causes scattered edits in many files. Put the parts that change together into one module.
- **Divergent Change**: One file or module gets edits for several unrelated reasons. Split it, so that each module changes for one reason.
- **Speculative Generality**: Abstraction, parameters or hooks for needs that the spec does not have. Remove it. Inline it again until a real need occurs.
- **Message Chains**: Long `a.b().c().d()` navigation that the caller should not depend on. Hide the navigation behind one method on the first object.
- **Middle Man**: A class or function that mostly only sends calls to a different target. Remove it, and call the real target directly.
- **Refused Bequest**: A subclass or implementer that ignores or overrides most of what it inherits. Remove the inheritance, and use composition.
