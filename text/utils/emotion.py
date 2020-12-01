import os.path
import warnings

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.ticker as tk

adverbs = {
           'Increase': ('absolutely', 'completely', 'incredibly', 'deeply',
                        'totally', 'fully', 'entirely', 'extremely', 'fairly',
                        'much', 'hardly', 'pretty', 'rather', 'really', 'so',
                        'too', 'very'),
           'Decrease': ('almost', 'barely', 'little', 'far',
 			            'just', 'nearly', 'only', 'quite', 'scarcely')
           }

pairs = {
         'joy': 'sadness', 'disgust': 'trust', 'fear': 'anger', 'surprise': 'anticipation',
         'sadness': 'joy', 'trust': 'disgust', 'anger': 'fear', 'anticipation': 'surprise',
         'positive': 'negative', 'negative': 'positive'
        }

colors = {
          'joy': '#ffbf00', 'sadness': '#00008B', 'trust': '#75ff2b',
          'disgust': '#d62173', 'fear': '#5cb270', 'anger': '#cc0000',
          'surprise': '#00BFFF', 'anticipation': '#e98121', 'negative': '#000000',
          'positive': '#f0a500'
         }

translateEmotion = {
                    'joy': 'alegria', 'sadness': 'tristeza', 'trust': 'confiança',
					'disgust': 'nojo/aversão', 'fear': 'medo', 'anger': 'raiva',
					'surprise': 'surpresa', 'anticipation': 'antecipação', 
					'negative': 'negativo', 'positive': 'positivo'
					}

def emotionGraphic(title, path, emotions, y, x = 0, fonts = {"supTitle": "Times New Roman",
                                                             "plot": "Times New Roman"},
                   extension = 'pdf', all = False, perChapter = False, barGraph = False):
    '''Generates a graph for emotions based on a dictionary.'''
    file = f'{path}/Emotions - {title}.{extension.lower()}'

    if os.path.isfile(file):
        n = 0
        while os.path.isfile(file):
            n += 1
            file = f'{path}/Emotions - {title} ({n}).{extension.lower()}'

    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams["font.family"] = fonts["plot"]

    if perChapter:
    	chapterNumber = [i for i in range(1, x+1)]

    if all:
        fig = plt.figure(figsize = (x, x/3))
        distanceTitle = 1.4
    else:
        rows = len(emotions)
        fig, figAxes = plt.subplots(ncols = 1, nrows = rows, figsize = (x, 3*x))
        fig.subplots_adjust(hspace = 1.5, wspace = 0.2)
        distanceTitle = 0.95

    mid = (fig.subplotpars.right + fig.subplotpars.left)/2
    fig.suptitle(title, x = mid, size = 60, y = distanceTitle, fontname = fonts["supTitle"])
    for row, emotion in enumerate(colors):
        if emotion in emotions:
            if all:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    axe = fig.add_subplot(1, 1, 1)
                plotTitle = 'Emoções'
            else:
                axe = figAxes[row]
                plotTitle = translateEmotion[emotion].capitalize()
            axe.spines['top'].set_visible(False)
            axe.spines['bottom'].set_visible(True)
            axe.spines['bottom'].set_color('black')
            axe.spines['right'].set_visible(False)
            axe.spines['left'].set_visible(True)
            axe.spines['left'].set_color('black')
            axe.get_xaxis().tick_bottom()
            axe.get_yaxis().tick_left()
            axe.grid(False)
            axe.yaxis.grid(True, 'major', ls = '--', lw = .7, c = 'k', alpha = .4)
            axe.tick_params(axis = 'both', which = 'both', labelsize = 35,
                            bottom = False, top = False, labelbottom = True,
                            left = False, right = False, labelleft = True,
                            pad = 20)
            axe.yaxis.set_major_locator(plt.MultipleLocator(2))
            axe.yaxis.set_major_formatter(tk.PercentFormatter(decimals = 0))
            axe.set_facecolor('#f7f7fa')

            if perChapter and not barGraph:
            	axe.plot(chapterNumber, y[emotion], color = f'{colors[emotion]}90',
    			         marker = 'o', linewidth = 4.5, label = translateEmotion[emotion].capitalize(),
    			         markerfacecolor = colors[emotion])
            	axe.set_title(plotTitle, fontsize = 50, y = 1.2)
            	axe.set_xlabel('Capítulos', fontsize = 30)
            	axe.xaxis.set_major_locator(plt.MultipleLocator(1))
            	axe.set_xlim(xmin = 1, xmax = x)
            	if not all:
            		axe.set_ylim(ymin = 0, ymax = max(y[emotion])+1)
            	else:
            		axe.legend(bbox_to_anchor = (1.02, 1), loc = 'upper left',
                               borderaxespad = 1,  fontsize = 30)
            elif perChapter and barGraph:
                axe.bar(x = chapterNumber, height = y[emotion], align = 'center',
                        color = f'{colors[emotion]}90', width = 0.5)
                axe.set_xticks(chapterNumber)
                axe.set_xticklabels(chapterNumber)
                axe.set_title(plotTitle, fontsize = 50, y = 1.2)
                axe.set_xlabel('Capítulos', fontsize = 30)
            else:
                axe.bar(x = emotion.capitalize(), height = y[emotion], align = 'center',
                        color = f'{colors[emotion]}90', width = 0.5)
    fig.savefig(file, bbox_inches = "tight", pad_inches = 3, dpi = 400)