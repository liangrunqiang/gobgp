# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: capability.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import gobgp_pb2 as gobgp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10\x63\x61pability.proto\x12\x05\x61pipb\x1a\x0bgobgp.proto\"8\n\x17MultiProtocolCapability\x12\x1d\n\x06\x66\x61mily\x18\x01 \x01(\x0b\x32\r.apipb.Family\"\x18\n\x16RouteRefreshCapability\"\x1d\n\x1b\x43\x61rryingLabelInfoCapability\"k\n\x1e\x45xtendedNexthopCapabilityTuple\x12\"\n\x0bnlri_family\x18\x01 \x01(\x0b\x32\r.apipb.Family\x12%\n\x0enexthop_family\x18\x02 \x01(\x0b\x32\r.apipb.Family\"R\n\x19\x45xtendedNexthopCapability\x12\x35\n\x06tuples\x18\x01 \x03(\x0b\x32%.apipb.ExtendedNexthopCapabilityTuple\"N\n\x1eGracefulRestartCapabilityTuple\x12\x1d\n\x06\x66\x61mily\x18\x01 \x01(\x0b\x32\r.apipb.Family\x12\r\n\x05\x66lags\x18\x02 \x01(\r\"o\n\x19GracefulRestartCapability\x12\r\n\x05\x66lags\x18\x01 \x01(\r\x12\x0c\n\x04time\x18\x02 \x01(\r\x12\x35\n\x06tuples\x18\x03 \x03(\x0b\x32%.apipb.GracefulRestartCapabilityTuple\"%\n\x16\x46ourOctetASNCapability\x12\x0b\n\x03\x61sn\x18\x01 \x01(\r\"\x9c\x01\n\x16\x41\x64\x64PathCapabilityTuple\x12\x1d\n\x06\x66\x61mily\x18\x01 \x01(\x0b\x32\r.apipb.Family\x12\x30\n\x04mode\x18\x02 \x01(\x0e\x32\".apipb.AddPathCapabilityTuple.Mode\"1\n\x04Mode\x12\x08\n\x04NONE\x10\x00\x12\x0b\n\x07RECEIVE\x10\x01\x12\x08\n\x04SEND\x10\x02\x12\x08\n\x04\x42OTH\x10\x03\"B\n\x11\x41\x64\x64PathCapability\x12-\n\x06tuples\x18\x01 \x03(\x0b\x32\x1d.apipb.AddPathCapabilityTuple\" \n\x1e\x45nhancedRouteRefreshCapability\"e\n\'LongLivedGracefulRestartCapabilityTuple\x12\x1d\n\x06\x66\x61mily\x18\x01 \x01(\x0b\x32\r.apipb.Family\x12\r\n\x05\x66lags\x18\x02 \x01(\r\x12\x0c\n\x04time\x18\x03 \x01(\r\"d\n\"LongLivedGracefulRestartCapability\x12>\n\x06tuples\x18\x01 \x03(\x0b\x32..apipb.LongLivedGracefulRestartCapabilityTuple\"\x1d\n\x1bRouteRefreshCiscoCapability\"8\n\x0e\x46qdnCapability\x12\x11\n\thost_name\x18\x01 \x01(\t\x12\x13\n\x0b\x64omain_name\x18\x02 \x01(\t\"0\n\x11UnknownCapability\x12\x0c\n\x04\x63ode\x18\x01 \x01(\r\x12\r\n\x05value\x18\x02 \x01(\x0c\x42$Z\"github.com/osrg/gobgp/v3/api;apipbb\x06proto3')



_MULTIPROTOCOLCAPABILITY = DESCRIPTOR.message_types_by_name['MultiProtocolCapability']
_ROUTEREFRESHCAPABILITY = DESCRIPTOR.message_types_by_name['RouteRefreshCapability']
_CARRYINGLABELINFOCAPABILITY = DESCRIPTOR.message_types_by_name['CarryingLabelInfoCapability']
_EXTENDEDNEXTHOPCAPABILITYTUPLE = DESCRIPTOR.message_types_by_name['ExtendedNexthopCapabilityTuple']
_EXTENDEDNEXTHOPCAPABILITY = DESCRIPTOR.message_types_by_name['ExtendedNexthopCapability']
_GRACEFULRESTARTCAPABILITYTUPLE = DESCRIPTOR.message_types_by_name['GracefulRestartCapabilityTuple']
_GRACEFULRESTARTCAPABILITY = DESCRIPTOR.message_types_by_name['GracefulRestartCapability']
_FOUROCTETASNCAPABILITY = DESCRIPTOR.message_types_by_name['FourOctetASNCapability']
_ADDPATHCAPABILITYTUPLE = DESCRIPTOR.message_types_by_name['AddPathCapabilityTuple']
_ADDPATHCAPABILITY = DESCRIPTOR.message_types_by_name['AddPathCapability']
_ENHANCEDROUTEREFRESHCAPABILITY = DESCRIPTOR.message_types_by_name['EnhancedRouteRefreshCapability']
_LONGLIVEDGRACEFULRESTARTCAPABILITYTUPLE = DESCRIPTOR.message_types_by_name['LongLivedGracefulRestartCapabilityTuple']
_LONGLIVEDGRACEFULRESTARTCAPABILITY = DESCRIPTOR.message_types_by_name['LongLivedGracefulRestartCapability']
_ROUTEREFRESHCISCOCAPABILITY = DESCRIPTOR.message_types_by_name['RouteRefreshCiscoCapability']
_FQDNCAPABILITY = DESCRIPTOR.message_types_by_name['FqdnCapability']
_UNKNOWNCAPABILITY = DESCRIPTOR.message_types_by_name['UnknownCapability']
_ADDPATHCAPABILITYTUPLE_MODE = _ADDPATHCAPABILITYTUPLE.enum_types_by_name['Mode']
MultiProtocolCapability = _reflection.GeneratedProtocolMessageType('MultiProtocolCapability', (_message.Message,), {
  'DESCRIPTOR' : _MULTIPROTOCOLCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.MultiProtocolCapability)
  })
_sym_db.RegisterMessage(MultiProtocolCapability)

RouteRefreshCapability = _reflection.GeneratedProtocolMessageType('RouteRefreshCapability', (_message.Message,), {
  'DESCRIPTOR' : _ROUTEREFRESHCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.RouteRefreshCapability)
  })
_sym_db.RegisterMessage(RouteRefreshCapability)

CarryingLabelInfoCapability = _reflection.GeneratedProtocolMessageType('CarryingLabelInfoCapability', (_message.Message,), {
  'DESCRIPTOR' : _CARRYINGLABELINFOCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.CarryingLabelInfoCapability)
  })
_sym_db.RegisterMessage(CarryingLabelInfoCapability)

ExtendedNexthopCapabilityTuple = _reflection.GeneratedProtocolMessageType('ExtendedNexthopCapabilityTuple', (_message.Message,), {
  'DESCRIPTOR' : _EXTENDEDNEXTHOPCAPABILITYTUPLE,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.ExtendedNexthopCapabilityTuple)
  })
_sym_db.RegisterMessage(ExtendedNexthopCapabilityTuple)

ExtendedNexthopCapability = _reflection.GeneratedProtocolMessageType('ExtendedNexthopCapability', (_message.Message,), {
  'DESCRIPTOR' : _EXTENDEDNEXTHOPCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.ExtendedNexthopCapability)
  })
_sym_db.RegisterMessage(ExtendedNexthopCapability)

GracefulRestartCapabilityTuple = _reflection.GeneratedProtocolMessageType('GracefulRestartCapabilityTuple', (_message.Message,), {
  'DESCRIPTOR' : _GRACEFULRESTARTCAPABILITYTUPLE,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.GracefulRestartCapabilityTuple)
  })
_sym_db.RegisterMessage(GracefulRestartCapabilityTuple)

GracefulRestartCapability = _reflection.GeneratedProtocolMessageType('GracefulRestartCapability', (_message.Message,), {
  'DESCRIPTOR' : _GRACEFULRESTARTCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.GracefulRestartCapability)
  })
_sym_db.RegisterMessage(GracefulRestartCapability)

FourOctetASNCapability = _reflection.GeneratedProtocolMessageType('FourOctetASNCapability', (_message.Message,), {
  'DESCRIPTOR' : _FOUROCTETASNCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.FourOctetASNCapability)
  })
_sym_db.RegisterMessage(FourOctetASNCapability)

AddPathCapabilityTuple = _reflection.GeneratedProtocolMessageType('AddPathCapabilityTuple', (_message.Message,), {
  'DESCRIPTOR' : _ADDPATHCAPABILITYTUPLE,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.AddPathCapabilityTuple)
  })
_sym_db.RegisterMessage(AddPathCapabilityTuple)

AddPathCapability = _reflection.GeneratedProtocolMessageType('AddPathCapability', (_message.Message,), {
  'DESCRIPTOR' : _ADDPATHCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.AddPathCapability)
  })
_sym_db.RegisterMessage(AddPathCapability)

EnhancedRouteRefreshCapability = _reflection.GeneratedProtocolMessageType('EnhancedRouteRefreshCapability', (_message.Message,), {
  'DESCRIPTOR' : _ENHANCEDROUTEREFRESHCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.EnhancedRouteRefreshCapability)
  })
_sym_db.RegisterMessage(EnhancedRouteRefreshCapability)

LongLivedGracefulRestartCapabilityTuple = _reflection.GeneratedProtocolMessageType('LongLivedGracefulRestartCapabilityTuple', (_message.Message,), {
  'DESCRIPTOR' : _LONGLIVEDGRACEFULRESTARTCAPABILITYTUPLE,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.LongLivedGracefulRestartCapabilityTuple)
  })
_sym_db.RegisterMessage(LongLivedGracefulRestartCapabilityTuple)

LongLivedGracefulRestartCapability = _reflection.GeneratedProtocolMessageType('LongLivedGracefulRestartCapability', (_message.Message,), {
  'DESCRIPTOR' : _LONGLIVEDGRACEFULRESTARTCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.LongLivedGracefulRestartCapability)
  })
_sym_db.RegisterMessage(LongLivedGracefulRestartCapability)

RouteRefreshCiscoCapability = _reflection.GeneratedProtocolMessageType('RouteRefreshCiscoCapability', (_message.Message,), {
  'DESCRIPTOR' : _ROUTEREFRESHCISCOCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.RouteRefreshCiscoCapability)
  })
_sym_db.RegisterMessage(RouteRefreshCiscoCapability)

FqdnCapability = _reflection.GeneratedProtocolMessageType('FqdnCapability', (_message.Message,), {
  'DESCRIPTOR' : _FQDNCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.FqdnCapability)
  })
_sym_db.RegisterMessage(FqdnCapability)

UnknownCapability = _reflection.GeneratedProtocolMessageType('UnknownCapability', (_message.Message,), {
  'DESCRIPTOR' : _UNKNOWNCAPABILITY,
  '__module__' : 'capability_pb2'
  # @@protoc_insertion_point(class_scope:apipb.UnknownCapability)
  })
_sym_db.RegisterMessage(UnknownCapability)

if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\"github.com/osrg/gobgp/v3/api;apipb'
  _MULTIPROTOCOLCAPABILITY._serialized_start=40
  _MULTIPROTOCOLCAPABILITY._serialized_end=96
  _ROUTEREFRESHCAPABILITY._serialized_start=98
  _ROUTEREFRESHCAPABILITY._serialized_end=122
  _CARRYINGLABELINFOCAPABILITY._serialized_start=124
  _CARRYINGLABELINFOCAPABILITY._serialized_end=153
  _EXTENDEDNEXTHOPCAPABILITYTUPLE._serialized_start=155
  _EXTENDEDNEXTHOPCAPABILITYTUPLE._serialized_end=262
  _EXTENDEDNEXTHOPCAPABILITY._serialized_start=264
  _EXTENDEDNEXTHOPCAPABILITY._serialized_end=346
  _GRACEFULRESTARTCAPABILITYTUPLE._serialized_start=348
  _GRACEFULRESTARTCAPABILITYTUPLE._serialized_end=426
  _GRACEFULRESTARTCAPABILITY._serialized_start=428
  _GRACEFULRESTARTCAPABILITY._serialized_end=539
  _FOUROCTETASNCAPABILITY._serialized_start=541
  _FOUROCTETASNCAPABILITY._serialized_end=578
  _ADDPATHCAPABILITYTUPLE._serialized_start=581
  _ADDPATHCAPABILITYTUPLE._serialized_end=737
  _ADDPATHCAPABILITYTUPLE_MODE._serialized_start=688
  _ADDPATHCAPABILITYTUPLE_MODE._serialized_end=737
  _ADDPATHCAPABILITY._serialized_start=739
  _ADDPATHCAPABILITY._serialized_end=805
  _ENHANCEDROUTEREFRESHCAPABILITY._serialized_start=807
  _ENHANCEDROUTEREFRESHCAPABILITY._serialized_end=839
  _LONGLIVEDGRACEFULRESTARTCAPABILITYTUPLE._serialized_start=841
  _LONGLIVEDGRACEFULRESTARTCAPABILITYTUPLE._serialized_end=942
  _LONGLIVEDGRACEFULRESTARTCAPABILITY._serialized_start=944
  _LONGLIVEDGRACEFULRESTARTCAPABILITY._serialized_end=1044
  _ROUTEREFRESHCISCOCAPABILITY._serialized_start=1046
  _ROUTEREFRESHCISCOCAPABILITY._serialized_end=1075
  _FQDNCAPABILITY._serialized_start=1077
  _FQDNCAPABILITY._serialized_end=1133
  _UNKNOWNCAPABILITY._serialized_start=1135
  _UNKNOWNCAPABILITY._serialized_end=1183
# @@protoc_insertion_point(module_scope)
