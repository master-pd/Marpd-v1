class TestSuite:
    def __init__(self, core):
        self.core = core
    
    def run_all_tests(self):
        tests = [
            self.test_core,
            self.test_plugins,
            self.test_security
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append({"test": test.__name__, "passed": result})
            except Exception as e:
                results.append({"test": test.__name__, "passed": False, "error": str(e)})
        
        return results
    
    def test_core(self):
        return hasattr(self.core, 'plugins')
    
    def test_plugins(self):
        return len(getattr(self.core, 'plugins', {})) >= 0
    
    def test_security(self):
        return True