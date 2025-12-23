# Kattistools
## Installation instructions:

In the root, run `python3 -m venv venv`, then run `venv/bin/pip install -r requirements.txt`.

After this, you can run the program by using bin/check_problem.sh. I would recommend adding the following
to your `.bashrc`: `alias check="clear && ~/software/kattistools/bin/check_problem.sh"` (where you replace
software with the folder you're using).

## Philosophy
Priorities:

- Minimizing false negatives. Therefore, false positives become more common.
- Don't add any metadata to problem packages. The only way that problem packages should change from
using this tool is that they are of higher quality.
- Checks should be cheap and run fast. It currently takes 5 seconds to check all 400 problems in my problems folder

## Example usage

`./bin/check_problem.sh ../swedish_olympiad_2016/katt1/cities`
```
> katt1/cities:
Errors:
source is 'Programmeringsolympiadens KATT 2016 - tävling 1', want 'Programmeringsolympiadens KATT 2016' (problem.yaml)
(sv) missing \section*{Indata} (statement)
(sv) missing \section*{Utdata} (statement)
Warnings:
(sv) Missing poängsättning-section (statement)
(sv) Did you forget "Inga ytterligare begränsningar." in subtask box? (statement)
(en) Missing scoring text (statement)
(en) missing modern subtask box problem.en.tex (statement)
(en) Did you forget "No additional constraints." in subtask box? (statement)
--------------
```

You can also use on a folder on a higher level, which will recursively discover all problems:

```
@:~/software/kattistools$ ./bin/check_problem.sh ../po/swedish-olympiad-2016/katt1/
> katt1/tshirts (include):
Errors:
source is 'Programmeringsolympiadens KATT 2016 - tävling 1', want 'Programmeringsolympiadens KATT 2016' (problem.yaml)
(sv) missing \section*{Indata} (statement)
(sv) missing \section*{Utdata} (statement)
(en) missing \section*{Input} (statement)
(en) missing \section*{Output} (statement)
input_format_validators is renamed to input_validators (Statement files)
Warnings:
(sv) Missing poängsättning-section (statement)
(sv) Did you forget "Inga ytterligare begränsningar." in subtask box? (statement)
(en) Missing \section*{Scoring} (statement)
(en) Missing scoring text (statement)
(en) missing modern subtask box problem.en.tex (statement)
(en) Did you forget "No additional constraints." in subtask box? (statement)
--------------


> katt1/magic (grader, include):
Errors:
source is 'Programmeringsolympiadens KATT 2016 - tävling 1', want 'Programmeringsolympiadens KATT 2016' (problem.yaml)
(sv) missing \section*{Indata} (statement)
(sv) missing \section*{Utdata} (statement)
(en) missing \section*{Input} (statement)
(en) missing \section*{Output} (statement)
input_format_validators is renamed to input_validators (Statement files)
Warnings:
.py file 'accepted/magic.py' does not start with shebang #!/usr/bin/python3 (check python has shebang)
(sv) Missing poängsättning-section (statement)
(sv) Did you forget "Inga ytterligare begränsningar." in subtask box? (statement)
(en) Missing \section*{Scoring} (statement)
(en) Missing scoring text (statement)
(en) missing modern subtask box problem.en.tex (statement)
(en) Did you forget "No additional constraints." in subtask box? (statement)
--------------


> katt1/friends3 (include):
Errors:
source is 'Programmeringsolympiadens KATT 2016 - tävling 1', want 'Programmeringsolympiadens KATT 2016' (problem.yaml)
(sv) missing \section*{Indata} (statement)
(sv) missing \section*{Utdata} (statement)
(en) missing \section*{Input} (statement)
(en) missing \section*{Output} (statement)
input_format_validators is renamed to input_validators (Statement files)
Warnings:
(sv) Missing poängsättning-section (statement)
(sv) Did you forget "Inga ytterligare begränsningar." in subtask box? (statement)
(en) Missing \section*{Scoring} (statement)
(en) Missing scoring text (statement)
(en) missing modern subtask box problem.en.tex (statement)
(en) Did you forget "No additional constraints." in subtask box? (statement)
--------------


> katt1/cities:
Errors:
source is 'Programmeringsolympiadens KATT 2016 - tävling 1', want 'Programmeringsolympiadens KATT 2016' (problem.yaml)
(sv) missing \section*{Indata} (statement)
(sv) missing \section*{Utdata} (statement)
Warnings:
(sv) Missing poängsättning-section (statement)
(sv) Did you forget "Inga ytterligare begränsningar." in subtask box? (statement)
(en) Missing scoring text (statement)
(en) missing modern subtask box problem.en.tex (statement)
(en) Did you forget "No additional constraints." in subtask box? (statement)
--------------

```

