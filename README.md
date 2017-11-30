# ISTEX_MentalRotation use-case of SSbE

## Repeatability code for SSbE paper of SERecSys Workshop of ICDM:

 - To start, you would need to generate the dataset using the script inside IstexDataDownload_Treatment folder (you may also dowload it from: ``https://drive.google.com/drive/folders/1i1I3fi6Qgdz-A4hI8_MkjZCg-EPieTi_?usp=sharing``)

 - The main file to start with is bow_svd.py. It will transform the whole corpus into its semantic features representation.

 - Then, run classifier.py to train and to generate ranked results.

 - The baseline is using More_Like_This Query of ElasticSearch.

 - You can find the users annotations in the annotations folder. The notebook comparatrive_evaluation.ipynb provide the initial evaluation

 - For active learning process, you should open and run the cells of build_dataset_active_learning.ipynb

 - You may also check other available notebooks for further analysis. Other .py files like LDA for topic analysis are also available
