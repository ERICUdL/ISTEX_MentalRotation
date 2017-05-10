# ISTEX_MentalRotation

Steps to run the experiment :

# build the classifier for the documents, according to the vectorisation done before
> python classifier.py (output: results/results.pickle)

# from the results of classified documents, build a dictionnary of documents : id:abstracts. This step should be removed to use directly the vectors given by the vectorizer.
> python ids2docs.py (output: results/LDA_res_input.pickle)

# Comput clusters on the documents well classified by the classifyer from the dictionnary given by ids2docs. 
> python LDACheck_key_phrases.py (output : results/results_lda.txt)

