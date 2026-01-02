# Copyright (c) 2025 OntoLogics (Seth & Axion). All rights reserved.
# Licensed under the VTR Public License (VTR-PL), Version 1.0.
#
# ==============================================================================
#                               LEGACY ARCHIVE
# ==============================================================================
# This file contains mothballed code related to the "V1 Economic Model" (DePIN,
# Tokens, Semantic Scores). It is preserved here for historical reference but is
# NOT used in the active VTR standard.
# ==============================================================================

from typing import Optional, Any, Dict
from pydantic import BaseModel, Field

class LegacyEconomicData(BaseModel):
    """
    [DEPRECATED] Former economic metadata structure.
    """
    semantic_score: float = Field(..., description="AI-generated value score of the content.")
    device_tier: str = Field(..., description="The tier of the capturing device (e.g., 'Gold', 'Potato').")
    payment_address: Optional[str] = Field(None, description="Wallet address for rewards.")
    network_id: str = Field("vtr-mainnet", description="The target settlement network.")
