#!/usr/bin/env python

"""
Created by: Lee Bergstrand (2019)

Description: A set of classes for generating an assignment database.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, Float, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class Sample(Base):
    """A table of samples representing genomes and metagenomes for which genome properties has been run on."""

    __tablename__ = 'samples'

    name = Column(String, primary_key=True)

    property_assignments = relationship('PropertyAssignment', back_populates='sample')

    def __repr__(self):
        return "<Sample(name='{}')>".format(self.name)


class PropertyAssignment(Base):
    """An assignment for a genome property (YES, NO, or PARTIAL)."""

    __tablename__ = 'property_assignments'

    assignment_identifier = Column(Integer, primary_key=True, autoincrement=True)
    property_identifier = Column(Integer)
    numeric_assignment = Column(Integer)  # 0 = YES, 1 = PARTIAL, 2 = NO
    sample_name = Column(String, ForeignKey('samples.name'))

    sample = relationship('Sample', back_populates='property_assignments')
    step_assignments = relationship('StepAssignment', back_populates='property_assignment')

    @property
    def assignment(self):
        """
        Converts assignments stored as integers to their word equivalent.
        :return: The assignment as a word.
        """
        assignment_type = self.numeric_assignment
        if assignment_type == 0:
            assignment = 'YES'
        elif assignment_type == 1:
            assignment = 'PARTIAL'
        else:
            assignment = 'NO'

        return assignment

    def __repr__(self):
        return "<PropertyAssignment(sample='{0:s}', name='GenProp{1:04d}', assignment='{2:s}')>".format(
            self.sample.name,
            self.property_identifier,
            self.assignment)


# A joining table to handle the many to many relationship between steps and InterProScan matches.
step_match_association_table = Table('step_interpro_identifiers', Base.metadata,
                                     Column('step_assignment_identifier', Integer,
                                            ForeignKey('step_assignments.step_assignment_identifier')),
                                     Column('interproscan_match_identifier', Integer,
                                            ForeignKey('interproscan_matchs.interproscan_match_identifier')))


class StepAssignment(Base):
    """An assignment for a genome property step. If present then it is assumed the step is present (e.g. YES)."""

    __tablename__ = 'step_assignments'

    step_assignment_identifier = Column(Integer, primary_key=True, autoincrement=True)
    property_assignment_identifier = Column(Integer, ForeignKey('property_assignments.assignment_identifier'))
    step_number = Column(Integer)

    property_assignment = relationship('PropertyAssignment', back_populates='step_assignments')
    interproscan_matches = relationship('InterProScanMatch', secondary=step_match_association_table,
                                        back_populates='step_assignments')

    def __repr__(self):
        return "<StepAssignment(Property='GenProp{0:04d}', number='{1:d}', assignment='YES')>".format(
            self.property_assignment.property_identifier,
            self.step_number)


class InterProScanMatch(Base):
    """Contains information about an InterProScan match supporting a step."""

    __tablename__ = 'interproscan_matchs'

    interproscan_match_identifier = Column(Integer, primary_key=True, autoincrement=True)
    sequence_identifier = Column(String, ForeignKey('sequence.identifier'))
    interpro_signature = Column(String)
    expected_value = Column(Float)

    step_assignments = relationship('StepAssignment', secondary=step_match_association_table,
                                    back_populates='interproscan_matches')
    sequence = relationship('Sequence', back_populates='matches')

    def __repr__(self):
        return "<InterProScanMatch(sequence_identifier='{0:s}', signature='{1:s}', assignment='{2:f}')>".format(
            self.sequence.identifier,
            self.interpro_signature,
            self.expected_value)


class Sequence(Base):
    """Contains information about protein sequence."""

    __tablename__ = 'sequence'

    identifier = Column(String, primary_key=True)
    sequence = Column(String)

    matches = relationship('InterProScanMatch', back_populates='sequence')

    def __repr__(self):
        return "<Sequence(identifier='{}')>".format(self.identifier)
