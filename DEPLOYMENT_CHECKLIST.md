# Deployment Checklist

Use this checklist before giving a build to an NGO or external tester.

## Clean-machine test

Test on a separate Windows computer that does not have Python installed.

- [ ] `ArSL_Sign_Recognition_Setup.exe` opens successfully.
- [ ] Installation completes without missing-file errors.
- [ ] Start Menu shortcut launches the app.
- [ ] Optional desktop shortcut launches the app.
- [ ] Loading screen appears immediately after launch.
- [ ] Main window opens after the model loads.
- [ ] Camera permission can be granted and the webcam preview appears.
- [ ] Hand bounding box appears.
- [ ] Sign recognition produces Arabic letters and confidence values.
- [ ] Add Letter, Delete, and Clear work.
- [ ] Written-form choices work for alef, waw, and ya variants.
- [ ] English/Arabic interface toggle works.
- [ ] App closes cleanly and releases the camera.
- [ ] Uninstall works from Windows Settings.

## User testing

For NGO testing, record feedback on:

- Ease of installation and startup.
- Whether instructions are understandable without technical help.
- Recognition reliability across different users and environments.
- Signs that are repeatedly confused.
- Camera positioning and lighting difficulties.
- Arabic wording and written-form selector clarity.
- Accessibility improvements requested by users.

Do not interpret controlled test accuracy as guaranteed real-world performance. Document any failure cases before wider deployment.
