# container-service-extension
# Copyright (c) 2020 VMware, Inc. All Rights Reserved.
# SPDX-License-Identifier: BSD-2-Clause
from dataclasses import asdict

from container_service_extension.common.constants.shared_constants import RequestKey  # noqa: E501
import container_service_extension.common.utils.server_utils as server_utils
import container_service_extension.lib.telemetry.constants as telemetry_constants  # noqa: E501
import container_service_extension.lib.telemetry.telemetry_handler as telemetry_handler  # noqa: E501
import container_service_extension.rde.backend.cluster_service_factory as cluster_service_factory  # noqa: E501
from container_service_extension.rde.models.abstractNativeEntity import AbstractNativeEntity  # noqa: E501
import container_service_extension.rde.models.rde_factory as rde_factory
import container_service_extension.security.context.operation_context as ctx
import container_service_extension.server.request_handlers.request_utils as request_utils  # noqa: E501


# TODO change api exception handler.
@telemetry_handler.record_user_action_telemetry(cse_operation=telemetry_constants.CseOperation.V36_CLUSTER_UPDATE)  # noqa: E501
@request_utils.v35_api_exception_handler
def cluster_update(data: dict, op_ctx: ctx.OperationContext):
    """Request handler for cluster resize operation.

    Validate data before actual resize is delegated to cluster service.

    :return: Defined entity of the native cluster
    :rtype: container_service_extension.def_.models.DefEntity
    """
    # TODO Reject request if rde_in_use is less than 2.0.0
    # TODO find out the RDE version from the request spec
    # TODO Insert RDE converters and validators
    cluster_id = data[RequestKey.CLUSTER_ID]
    rde_in_use = server_utils.get_rde_version_in_use()
    svc = cluster_service_factory.ClusterServiceFactory(op_ctx). \
        get_cluster_service(rde_in_use)
    NativeEntityClass = rde_factory.get_rde_model(rde_in_use)
    cluster_entity_spec: AbstractNativeEntity = \
        NativeEntityClass(**data[RequestKey.INPUT_SPEC])  # noqa: E501
    curr_entity = svc.entity_svc.get_entity(cluster_id)
    is_upgrade_operation = \
        request_utils.validate_cluster_update_request_and_check_cluster_upgrade(  # noqa: E501
            asdict(cluster_entity_spec.spec), asdict(curr_entity.entity.spec))
    if is_upgrade_operation:
        return asdict(svc.upgrade_cluster(cluster_id, cluster_entity_spec))
    return asdict(svc.resize_cluster(cluster_id, cluster_entity_spec))
