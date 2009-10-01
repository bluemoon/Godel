from svm import *

def svm_main(container):
    final = []
    for word in container.words:
        cur = word.items()
        final.append({(cur[0][0]):(tags[cur[0][1]]/100.0)})

    print final
    param = svm_parameter(kernel_type = LINEAR, C = 100)
    labels  = []
    for i in range(len(final)):
        labels.append(i)
    
    samples = final
    prob = svm_problem(labels, samples)
    m = svm_model(prob, param)
    #target = cross_validation(prob, param, n)
    #d = m.predict_values([1])
    #print d
    prd, prb = m.predict_probability([1])
