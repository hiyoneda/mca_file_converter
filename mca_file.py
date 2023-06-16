#!/usr/bin/env python
# coding: UTF-8

import sys
import ROOT
import yaml
import numpy as np

class MCAfile:
    filename = "test.mca"
    
    pmca_spectrum = {}
    data = []

    dp5_configuration = {}
    dpp_status = {}

    def __init__(self):
        pass

    def convert_value(self, value):
        try:
            return int(value)
        except:
            pass

        try:
            return float(value)
        except:
            pass

        return value

    def update_status(self, status, line):
        if line == "<<PMCA SPECTRUM>>\n":
            return 1
        elif line == "<<DATA>>\n":
            return 2
        elif line == "<<END>>\n":
            return 0
        elif line == "<<DP5 CONFIGURATION>>\n":
            return 3
        elif line == "<<DP5 CONFIGURATION END>>\n":
            return 0
        elif line == "<<DPP STATUS>>\n":
            return 4
        elif line == "<<DPP STATUS END>>\n":
            return 0

        return status

    def load_data(self):

        with open(self.filename, "r", encoding="Shift-JIS") as f:
            status = 0
            for line in f:
                new_status = self.update_status(status, line)

                if status != new_status:
                    status = new_status

                else:
                    if status == 0:
                        pass

                    elif status == 1: # PMCA SPECTRUM
                        _  = line.split(" - ")
                        key = _[0]
                        value = _[1].replace("\n", "")
                        self.pmca_spectrum[key] = self.convert_value(value)

                    elif status == 2: # DATA
                        self.data.append(int(line))

                    elif status == 3: # DP5 CONFIGURATION
                        _  = line.split(";")[0].split("=")
                        key = _[0]
                        value = _[1]
                        self.dp5_configuration[key] = self.convert_value(value)

                    elif status == 4: # DPP STATUS
                        _  = line.split(": ")
                        key = _[0]
                        value = _[1].replace("\n", "")
                        self.dpp_status[key] = self.convert_value(value)

    def save_histogram(self, outfilename, histname = "mca_spectrum"):
        nbin = len(self.data)

        rootfile = ROOT.TFile(outfilename, "recreate")

        histogram = ROOT.TH1D(histname, histname + ";ADC;Counts", nbin, 0, nbin)

        for ibin in range(nbin):
            histogram.SetBinContent(ibin+1, self.data[ibin])

        rootfile.cd()
        histogram.Write()
        rootfile.Close()

    def save_parameterfile(self, outfilename):
        data = {"pmca_spectrum": self.pmca_spectrum, "dp5_configuration": self.dp5_configuration, "dpp_status": self.dpp_status}

        with open(file=outfilename, mode='w', encoding='utf-8') as f:
            yaml.dump(data=data, stream=f, allow_unicode=True, sort_keys=False)

    def save_all(self, filename_header = None, histname = "mca_spectrum"):
        if filename_header is None:
            filename_header = self.filename
        self.save_histogram(filename_header + ".root", histname)
        self.save_parameterfile(filename_header + ".param.txt")

if __name__=="__main__":
    test = MCAfile()
    test.filename = sys.argv[1]
    test.load_data()
    test.save_all()
