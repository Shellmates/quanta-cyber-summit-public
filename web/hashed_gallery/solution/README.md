# Challenge name

## Write-up

The idea is to find a way to inject code into the `${when}` variable, which is used in the Pug templates without proper sanitization. By submitting a feedback form with a specially crafted `when` value, we can execute arbitrary JavaScript code on the server.

Since the use of ES6 modules, we can't use the `require` function directly which means that also `process.mainModule.constructor._load` is not available

, but we can access the `process.binding` function to interact with the filesystem. By injecting code that calls `process.binding("fs").readdir(".",0,0o666)`, we can list the files in the current directory. Then, we can read the contents of the `flag.txt` file using `process.binding('fs').readFileUtf8("/app/flag.txt",0,0o666)`.

The idea behind the challenge is to demonstrate how server-side template injection (SSTI) can lead to remote code execution (RCE) if user input is not properly sanitized, but also to show how the use of ES6 modules can affect the attack surface and require different techniques to achieve the same goal.

The usage of ES6 modules was intentional to make the challenge more interesting and to encourage participants to think creatively about how to bypass the restrictions imposed by the module system. It also highlights the importance of understanding the underlying technologies and their security implications when developing web applications.


## Note

Since this challenge include SSTI vulnerability which is RCE, many unintended solutions are possible, the one described in the write-up is just one of them, and there are many other ways to achieve the same goal.


All other paths are trolling paths or dead ends, and the intended solution is the one described in the write-up.
## Flag

`shellmates{sSTi_wiTH_Es6_MoDuleS_noT_A_baD_iDEa}`
