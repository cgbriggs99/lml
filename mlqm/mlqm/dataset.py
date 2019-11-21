#!/usr/bin/python3

from . import base
import json
import numpy as np

class JsonDatasetBuilder(base.DatasetBuilder) :
    """
    JsonDatasetBuiler

    This class represents a builder that grabs variables from a JSON file.

    Contributors: Connor Briggs, Ben Peyton

    Methods
    -------
    See base.DatasetBuilder

    build
        Build the dataset.
    """

    def build(self, dlist, outfile, varnames) :
        """
        JsonDatasetBuilder.build

        Build the dataset.

        Contributors: Connor Briggs, Ben Peyton

        Parameters
        ----------
        dlist
            The list of directories to look for json files.

        outfile
            The name of the file to look for in each directory.

        varnames
            An iterable of variable names to retrieve from the json files.

        Returns
        -------
        base.Dataset
            The dataset.
        """
        rdict = base.Dataset()
        for varname in varnames:
            rdict[varname] = {}
            for dname in dlist:
                with open(dname + "/" + outfile) as out:
                    jout = json.load(out)
                    rdict[varname][dname] = jout[varname]
        return rdict

class NumpyDatasetBuilder(base.DatasetBuilder) :
    """
    NumpyDatasetBuilder

    Builds a dataset using numpy saves to collect input.

    Contributors: Connor Briggs, Ben Peyton

    Methods
    -------
    See base.DatasetBuilder
    """

    def build(self, dlist, fnames) :
        """
        NumpyDatasetBuilder

        Builds a dataset using numpy save files

        Contributors: Connor Briggs, Ben Peyton

        Parameters
        ----------
        dlist
            The list of directories to look for data in.

        fnames
            The list of filenames to search for in each directory. These
            will also be used for dictionary labels.

        Returns
        -------
        base.Dataset
            The dataset.
        """
        rdict = base.Dataset()
        for fname in fnames:
            rdict[fname] = {}
        
        for dname in dlist:
            for fname in fnames :
                rdict[fname][dname] = np.load(dname + '/' + fname)
