
# Final contract normalization after all functional/widget patches have been applied.
test_path=root/'tests/desktop_contract_test.js'
test=test_path.read_text()
old="ok(app.includes('function shell(){\\n  applyRoot();'),'shell root route update');"
new="ok(app.includes('function shell(){')&&app.includes('applyRoot();')&&app.includes('if(widgetMode)return renderWidget()'),'shell root route update');"
if old in test:
    test=test.replace(old,new,1)
elif new not in test:
    raise RuntimeError('shell root contract assertion marker missing')
test_path.write_text(test)
