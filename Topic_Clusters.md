# ISTEX_MentalRotation

Steps to run the experiment :
ISTEX_MentalRotation/>  python bow_svd

- build the classifier for the documents

ISTEX_MentalRotation/> python classifier.py 

(output: results/results.pickle)

- from the results of classified documents, build a dictionnary of documents : id:abstracts. This step should be removed to use directly the vectors given by the vectorizer.

ISTEX_MentalRotation/>  python ids2docs.py 

(output: results/LDA_res_input.pickle)

- Compute clusters on the documents well classified by the classifier from the dictionnary given by ids2docs.

ISTEX_MentalRotation/>  python Topic_Clustering.py 

(output : results/results_lda.txt)

