from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from database.repository import Persistence
from globals import *
from database.models import  PredefinedRuleEntity

import json


analyzer = AnalyzerEngine()
engine = AnonymizerEngine()



class presidio_wrapper:
    def analyze_message(message):
        # Set up the engine, loads the NLP module (spaCy model by default)
        # and other PII recognizers
        
        # Get all enabled entities from predefined_rules table
        enabled_entities=Persistence.get_all_enabled_entities(PredefinedRuleEntity,'presidio')
        
        # Call analyzer to get results
        results = analyzer.analyze(
            text=message, entities=enabled_entities, language="en"
        )
        return results
        

    def anonymyze_message(message, analysis):
        result = engine.anonymize(
            text=message, analyzer_results=analysis
        )
        return result.text
    